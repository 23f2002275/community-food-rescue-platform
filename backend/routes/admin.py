from flask import Blueprint, request, jsonify
from flask_security import auth_required, roles_required
from sqlalchemy import func
from extensions import db
from security_setup import user_datastore
from models import User, FoodListing, Reservation

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def users():
    query = User.query
    keyword = str(request.args.get('keyword', '')).strip()
    if keyword:
        query = query.filter((User.name.ilike(f'%{keyword}%')) | (User.email.ilike(f'%{keyword}%')))
    return jsonify([user.to_dict() for user in query.order_by(User.created_at.desc()).all()]), 200

@admin_bp.route('/users/<int:user_id>/active', methods=['PATCH'])
@auth_required('token')
@roles_required('admin')
def update_user_active(user_id):
    user = User.query.get_or_404(user_id)
    active = bool((request.get_json() or {}).get('active'))

    if active:
        user_datastore.activate_user(user)
    else:
        user_datastore.deactivate_user(user)

    db.session.commit()
    return jsonify({'message': 'User status updated', 'user': user.to_dict()}), 200

@admin_bp.route('/listings', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def listings():
    items = FoodListing.query.order_by(FoodListing.created_at.desc()).all()
    return jsonify([item.to_dict(True) for item in items]), 200

@admin_bp.route('/listings/<int:listing_id>/visibility', methods=['PATCH'])
@auth_required('token')
@roles_required('admin')
def listing_visibility(listing_id):
    listing = FoodListing.query.get_or_404(listing_id)
    visible = bool((request.get_json() or {}).get('visible'))

    if visible:
        listing.status = 'ACTIVE'
    else:
        listing.status = 'HIDDEN'

    db.session.commit()
    return jsonify({'message': 'Listing visibility updated', 'listing': listing.to_dict(True)}), 200

@admin_bp.route('/statistics', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def statistics():
    collected_quantity = db.session.query(func.coalesce(func.sum(Reservation.requested_quantity), 0)).filter(Reservation.status == 'COLLECTED').scalar()
    return jsonify({
        'users': User.query.count(),
        'donors': User.query.filter(User.roles.any(name='donor')).count(),
        'receivers': User.query.filter(User.roles.any(name='receiver')).count(),
        'listings': FoodListing.query.count(),
        'active_listings': FoodListing.query.filter_by(status='ACTIVE').count(),
        'reservations': Reservation.query.count(),
        'collected_pickups': Reservation.query.filter_by(status='COLLECTED').count(),
        'collected_quantity': collected_quantity
    }), 200
