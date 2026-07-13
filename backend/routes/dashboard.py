from flask import Blueprint, jsonify
from flask_security import auth_required, current_user
from sqlalchemy import func
from models import User, FoodListing, Reservation

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('', methods=['GET'])
@auth_required('token')
def dashboard():
    if current_user.has_role('donor'):
        listings = FoodListing.query.filter_by(donor_id=current_user.id)
        reservations = Reservation.query.join(FoodListing).filter(FoodListing.donor_id == current_user.id)
        data = {
            'role': 'donor',
            'active_listings': listings.filter_by(status='ACTIVE').count(),
            'total_listings': listings.count(),
            'pending_requests': reservations.filter(Reservation.status == 'PENDING').count(),
            'completed_pickups': reservations.filter(Reservation.status == 'COLLECTED').count(),
            'quantity_donated': reservations.filter(Reservation.status == 'COLLECTED').with_entities(func.coalesce(func.sum(Reservation.requested_quantity), 0)).scalar(),
            'recent': [item.to_dict() for item in reservations.order_by(Reservation.requested_at.desc()).limit(5).all()]
        }
    elif current_user.has_role('receiver'):
        reservations = Reservation.query.filter_by(receiver_id=current_user.id)
        data = {
            'role': 'receiver',
            'pending_requests': reservations.filter_by(status='PENDING').count(),
            'approved_requests': reservations.filter_by(status='APPROVED').count(),
            'collected_requests': reservations.filter_by(status='COLLECTED').count(),
            'cancelled_requests': reservations.filter_by(status='CANCELLED').count(),
            'recent': [item.to_dict() for item in reservations.order_by(Reservation.requested_at.desc()).limit(5).all()]
        }
    else:
        data = {
            'role': 'admin',
            'users': User.query.count(),
            'active_listings': FoodListing.query.filter_by(status='ACTIVE').count(),
            'reservations': Reservation.query.count(),
            'collected': Reservation.query.filter_by(status='COLLECTED').count(),
            'recent': [item.to_dict() for item in Reservation.query.order_by(Reservation.requested_at.desc()).limit(5).all()]
        }

    return jsonify(data), 200
