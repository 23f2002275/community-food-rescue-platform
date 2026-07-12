from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user, roles_required
from sqlalchemy import or_
from extensions import db
from models import FoodListing

listings_bp = Blueprint('listings', __name__)

def parse_datetime(value):
    try:
        return datetime.fromisoformat(str(value).replace('Z', '+00:00')).replace(tzinfo=None)
    except (TypeError, ValueError):
        return None

def can_manage(listing):
    return listing.donor_id == current_user.id or current_user.has_role('admin')

@listings_bp.route('', methods=['GET'])
def get_listings():
    query = FoodListing.query.filter(
        FoodListing.status == 'ACTIVE',
        FoodListing.expiry_time > datetime.utcnow(),
        FoodListing.available_quantity > 0
    )

    keyword = str(request.args.get('keyword', '')).strip()
    food_type = str(request.args.get('food_type', '')).strip()
    dietary_tag = str(request.args.get('dietary_tag', '')).strip()
    location = str(request.args.get('location', '')).strip()

    if keyword:
        query = query.filter(or_(FoodListing.title.ilike(f'%{keyword}%'), FoodListing.description.ilike(f'%{keyword}%')))
    if food_type:
        query = query.filter(FoodListing.food_type == food_type)
    if dietary_tag:
        query = query.filter(FoodListing.dietary_tag == dietary_tag)
    if location:
        query = query.filter(FoodListing.pickup_location.ilike(f'%{location}%'))

    page = max(int(request.args.get('page', 1)), 1)
    per_page = min(max(int(request.args.get('per_page', 9)), 1), 50)
    result = query.order_by(FoodListing.expiry_time.asc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [listing.to_dict() for listing in result.items],
        'page': result.page,
        'pages': result.pages,
        'total': result.total
    }), 200

@listings_bp.route('/mine', methods=['GET'])
@auth_required('token')
@roles_required('donor')
def my_listings():
    listings = FoodListing.query.filter_by(donor_id=current_user.id).order_by(FoodListing.created_at.desc()).all()
    return jsonify([listing.to_dict(True) for listing in listings]), 200

@listings_bp.route('/<int:listing_id>', methods=['GET'])
def get_listing(listing_id):
    listing = FoodListing.query.get_or_404(listing_id)
    if listing.status == 'HIDDEN':
        return jsonify({'message': 'Listing is not available'}), 404
    data = listing.to_dict(True)
    data['reviews'] = [review.to_dict() for reservation in listing.reservations for review in reservation.reviews]
    return jsonify(data), 200

@listings_bp.route('', methods=['POST'])
@auth_required('token')
@roles_required('donor')
def create_listing():
    data = request.get_json() or {}
    required = ['title', 'food_type', 'total_quantity', 'unit', 'pickup_location', 'expiry_time']

    if any(data.get(field) in [None, ''] for field in required):
        return jsonify({'message': 'Required listing fields are missing'}), 400

    try:
        quantity = int(data.get('total_quantity'))
    except (TypeError, ValueError):
        return jsonify({'message': 'Quantity must be a number'}), 400

    expiry_time = parse_datetime(data.get('expiry_time'))
    status = str(data.get('status', 'DRAFT')).upper()

    if quantity <= 0:
        return jsonify({'message': 'Quantity must be positive'}), 400
    if not expiry_time:
        return jsonify({'message': 'Invalid expiry time'}), 400
    if status not in ['DRAFT', 'ACTIVE']:
        return jsonify({'message': 'Status must be DRAFT or ACTIVE'}), 400
    if status == 'ACTIVE' and expiry_time <= datetime.utcnow():
        return jsonify({'message': 'Expiry time must be in the future'}), 400

    listing = FoodListing(
        donor_id=current_user.id,
        title=str(data.get('title')).strip(),
        description=str(data.get('description', '')).strip(),
        food_type=str(data.get('food_type')).strip(),
        dietary_tag=str(data.get('dietary_tag', '')).strip(),
        total_quantity=quantity,
        available_quantity=quantity,
        unit=str(data.get('unit')).strip(),
        pickup_location=str(data.get('pickup_location')).strip(),
        pickup_notes=str(data.get('pickup_notes', '')).strip(),
        expiry_time=expiry_time,
        status=status
    )
    db.session.add(listing)
    db.session.commit()

    return jsonify({'message': 'Listing created', 'listing': listing.to_dict(True)}), 201

@listings_bp.route('/<int:listing_id>', methods=['PUT'])
@auth_required('token')
def update_listing(listing_id):
    listing = FoodListing.query.get_or_404(listing_id)

    if not can_manage(listing):
        return jsonify({'message': 'You cannot edit this listing'}), 403

    if listing.status in ['CLOSED', 'EXPIRED', 'HIDDEN'] and not current_user.has_role('admin'):
        return jsonify({'message': 'This listing cannot be edited'}), 409

    data = request.get_json() or {}
    expiry_time = parse_datetime(data.get('expiry_time', listing.expiry_time.isoformat()))

    if not expiry_time or expiry_time <= datetime.utcnow():
        return jsonify({'message': 'Expiry time must be in the future'}), 400

    try:
        total_quantity = int(data.get('total_quantity', listing.total_quantity))
    except (TypeError, ValueError):
        return jsonify({'message': 'Quantity must be a number'}), 400

    reserved = listing.total_quantity - listing.available_quantity
    if total_quantity <= 0 or total_quantity < reserved:
        return jsonify({'message': 'Quantity cannot be lower than approved quantity'}), 400

    listing.title = str(data.get('title', listing.title)).strip()
    listing.description = str(data.get('description', listing.description or '')).strip()
    listing.food_type = str(data.get('food_type', listing.food_type)).strip()
    listing.dietary_tag = str(data.get('dietary_tag', listing.dietary_tag or '')).strip()
    listing.available_quantity += total_quantity - listing.total_quantity
    listing.total_quantity = total_quantity
    listing.unit = str(data.get('unit', listing.unit)).strip()
    listing.pickup_location = str(data.get('pickup_location', listing.pickup_location)).strip()
    listing.pickup_notes = str(data.get('pickup_notes', listing.pickup_notes or '')).strip()
    listing.expiry_time = expiry_time
    db.session.commit()

    return jsonify({'message': 'Listing updated', 'listing': listing.to_dict(True)}), 200

@listings_bp.route('/<int:listing_id>', methods=['DELETE'])
@auth_required('token')
def delete_listing(listing_id):
    listing = FoodListing.query.get_or_404(listing_id)

    if not can_manage(listing):
        return jsonify({'message': 'You cannot delete this listing'}), 403
    if listing.reservations:
        return jsonify({'message': 'Listing has reservation history and cannot be deleted'}), 409

    db.session.delete(listing)
    db.session.commit()
    return '', 204

@listings_bp.route('/<int:listing_id>/status', methods=['PATCH'])
@auth_required('token')
def update_status(listing_id):
    listing = FoodListing.query.get_or_404(listing_id)

    if not can_manage(listing):
        return jsonify({'message': 'You cannot change this listing'}), 403

    status = str((request.get_json() or {}).get('status', '')).upper()

    if current_user.has_role('admin'):
        allowed = ['ACTIVE', 'CLOSED', 'HIDDEN']
    else:
        allowed = ['ACTIVE', 'CLOSED']

    if status not in allowed:
        return jsonify({'message': 'Invalid status'}), 400
    if status == 'ACTIVE' and listing.expiry_time <= datetime.utcnow():
        return jsonify({'message': 'Expired listing cannot be activated'}), 409

    listing.status = status
    db.session.commit()
    return jsonify({'message': 'Status updated', 'listing': listing.to_dict(True)}), 200
