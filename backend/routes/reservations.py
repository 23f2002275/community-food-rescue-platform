from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user, roles_required
from extensions import db
from models import FoodListing, Reservation, Review

reservations_bp = Blueprint('reservations', __name__)

@reservations_bp.route('/listings/<int:listing_id>/reservations', methods=['POST'])
@auth_required('token')
@roles_required('receiver')
def create_reservation(listing_id):
    listing = FoodListing.query.get_or_404(listing_id)
    data = request.get_json() or {}

    if listing.status != 'ACTIVE' or listing.expiry_time <= datetime.utcnow():
        return jsonify({'message': 'Listing is not active'}), 409
    if listing.donor_id == current_user.id:
        return jsonify({'message': 'You cannot reserve your own listing'}), 400

    try:
        quantity = int(data.get('requested_quantity'))
    except (TypeError, ValueError):
        return jsonify({'message': 'Quantity must be a number'}), 400

    if quantity <= 0 or quantity > listing.available_quantity:
        return jsonify({'message': 'Requested quantity is not available'}), 400

    existing = Reservation.query.filter(
        Reservation.listing_id == listing.id,
        Reservation.receiver_id == current_user.id,
        Reservation.status.in_(['PENDING', 'APPROVED'])
    ).first()

    if existing:
        return jsonify({'message': 'You already have an active request for this listing'}), 409

    reservation = Reservation(
        listing_id=listing.id,
        receiver_id=current_user.id,
        requested_quantity=quantity,
        message=str(data.get('message', '')).strip()
    )
    db.session.add(reservation)
    db.session.commit()

    return jsonify({'message': 'Reservation requested', 'reservation': reservation.to_dict()}), 201

@reservations_bp.route('/reservations/mine', methods=['GET'])
@auth_required('token')
def my_reservations():
    if current_user.has_role('donor'):
        reservations = Reservation.query.join(FoodListing).filter(FoodListing.donor_id == current_user.id)
    elif current_user.has_role('receiver'):
        reservations = Reservation.query.filter_by(receiver_id=current_user.id)
    else:
        reservations = Reservation.query

    status = str(request.args.get('status', '')).upper()
    if status:
        reservations = reservations.filter(Reservation.status == status)

    items = reservations.order_by(Reservation.requested_at.desc()).all()
    return jsonify([item.to_dict() for item in items]), 200

@reservations_bp.route('/reservations/<int:reservation_id>', methods=['GET'])
@auth_required('token')
def get_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    participant = reservation.receiver_id == current_user.id or reservation.listing.donor_id == current_user.id

    if not participant and not current_user.has_role('admin'):
        return jsonify({'message': 'You cannot view this reservation'}), 403

    data = reservation.to_dict()
    data['reviews'] = [review.to_dict() for review in reservation.reviews]
    return jsonify(data), 200

@reservations_bp.route('/reservations/<int:reservation_id>/approve', methods=['PATCH'])
@auth_required('token')
@roles_required('donor')
def approve_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    listing = reservation.listing

    if listing.donor_id != current_user.id:
        return jsonify({'message': 'You cannot approve this request'}), 403
    if reservation.status != 'PENDING':
        return jsonify({'message': 'Only pending requests can be approved'}), 409
    if listing.status != 'ACTIVE' or listing.expiry_time <= datetime.utcnow():
        return jsonify({'message': 'Listing is no longer active'}), 409
    if reservation.requested_quantity > listing.available_quantity:
        return jsonify({'message': 'Not enough quantity is available'}), 409

    listing.available_quantity -= reservation.requested_quantity
    reservation.status = 'APPROVED'
    reservation.decided_at = datetime.utcnow()

    if listing.available_quantity == 0:
        listing.status = 'CLOSED'

    db.session.commit()
    return jsonify({'message': 'Reservation approved', 'reservation': reservation.to_dict()}), 200

@reservations_bp.route('/reservations/<int:reservation_id>/reject', methods=['PATCH'])
@auth_required('token')
@roles_required('donor')
def reject_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)

    if reservation.listing.donor_id != current_user.id:
        return jsonify({'message': 'You cannot reject this request'}), 403
    if reservation.status != 'PENDING':
        return jsonify({'message': 'Only pending requests can be rejected'}), 409

    reservation.status = 'REJECTED'
    reservation.decided_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Reservation rejected', 'reservation': reservation.to_dict()}), 200

@reservations_bp.route('/reservations/<int:reservation_id>/cancel', methods=['PATCH'])
@auth_required('token')
def cancel_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    listing = reservation.listing
    is_receiver = reservation.receiver_id == current_user.id
    is_donor = listing.donor_id == current_user.id

    if not is_receiver and not is_donor and not current_user.has_role('admin'):
        return jsonify({'message': 'You cannot cancel this request'}), 403
    if reservation.status not in ['PENDING', 'APPROVED']:
        return jsonify({'message': 'This request cannot be cancelled'}), 409

    if reservation.status == 'APPROVED':
        listing.available_quantity += reservation.requested_quantity
        if listing.status == 'CLOSED' and listing.expiry_time > datetime.utcnow():
            listing.status = 'ACTIVE'

    reservation.status = 'CANCELLED'
    db.session.commit()
    return jsonify({'message': 'Reservation cancelled', 'reservation': reservation.to_dict()}), 200

@reservations_bp.route('/reservations/<int:reservation_id>/collect', methods=['PATCH'])
@auth_required('token')
def collect_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)

    if reservation.listing.donor_id != current_user.id and not current_user.has_role('admin'):
        return jsonify({'message': 'You cannot mark this pickup collected'}), 403
    if reservation.status != 'APPROVED':
        return jsonify({'message': 'Only approved requests can be collected'}), 409

    reservation.status = 'COLLECTED'
    reservation.collected_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Pickup marked collected', 'reservation': reservation.to_dict()}), 200

@reservations_bp.route('/reservations/<int:reservation_id>/reviews', methods=['POST'])
@auth_required('token')
def create_review(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    participant = reservation.receiver_id == current_user.id or reservation.listing.donor_id == current_user.id

    if not participant:
        return jsonify({'message': 'Only participants can review'}), 403
    if reservation.status != 'COLLECTED':
        return jsonify({'message': 'Review is allowed after collection'}), 409
    if Review.query.filter_by(reservation_id=reservation.id, reviewer_id=current_user.id).first():
        return jsonify({'message': 'You already reviewed this reservation'}), 409

    data = request.get_json() or {}
    try:
        rating = int(data.get('rating'))
    except (TypeError, ValueError):
        return jsonify({'message': 'Rating must be a number'}), 400

    if rating < 1 or rating > 5:
        return jsonify({'message': 'Rating must be between 1 and 5'}), 400

    review = Review(
        reservation_id=reservation.id,
        reviewer_id=current_user.id,
        rating=rating,
        comment=str(data.get('comment', '')).strip()
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({'message': 'Review added', 'review': review.to_dict()}), 201
