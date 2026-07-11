from datetime import datetime
from flask_security import UserMixin, RoleMixin
from extensions import db

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    listings = db.relationship('FoodListing', backref='donor', lazy=True, foreign_keys='FoodListing.donor_id')
    reservations = db.relationship('Reservation', backref='receiver', lazy=True, foreign_keys='Reservation.receiver_id')

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'address': self.address,
            'active': self.active,
            'roles': [role.name for role in self.roles],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class FoodListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    food_type = db.Column(db.String(80), nullable=False)
    dietary_tag = db.Column(db.String(80))
    total_quantity = db.Column(db.Integer, nullable=False)
    available_quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(30), nullable=False)
    pickup_location = db.Column(db.String(255), nullable=False)
    pickup_notes = db.Column(db.Text)
    expiry_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(30), default='DRAFT')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reservations = db.relationship('Reservation', backref='listing', lazy=True)

    def to_dict(self, details=False):
        data = {
            'id': self.id,
            'donor_id': self.donor_id,
            'donor_name': self.donor.name if self.donor else None,
            'title': self.title,
            'food_type': self.food_type,
            'dietary_tag': self.dietary_tag,
            'total_quantity': self.total_quantity,
            'available_quantity': self.available_quantity,
            'unit': self.unit,
            'pickup_location': self.pickup_location,
            'expiry_time': self.expiry_time.isoformat() if self.expiry_time else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if details:
            data['description'] = self.description
            data['pickup_notes'] = self.pickup_notes
            data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        return data

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('food_listing.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    requested_quantity = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.String(30), default='PENDING')
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    decided_at = db.Column(db.DateTime)
    collected_at = db.Column(db.DateTime)
    reviews = db.relationship('Review', backref='reservation', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'listing_id': self.listing_id,
            'listing_title': self.listing.title if self.listing else None,
            'donor_id': self.listing.donor_id if self.listing else None,
            'donor_name': self.listing.donor.name if self.listing and self.listing.donor else None,
            'receiver_id': self.receiver_id,
            'receiver_name': self.receiver.name if self.receiver else None,
            'requested_quantity': self.requested_quantity,
            'unit': self.listing.unit if self.listing else None,
            'message': self.message,
            'status': self.status,
            'requested_at': self.requested_at.isoformat() if self.requested_at else None,
            'decided_at': self.decided_at.isoformat() if self.decided_at else None,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None,
            'reviewed_by': [review.reviewer_id for review in self.reviews]
        }

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])
    __table_args__ = (db.UniqueConstraint('reservation_id', 'reviewer_id', name='unique_reservation_reviewer'),)

    def to_dict(self):
        return {
            'id': self.id,
            'reservation_id': self.reservation_id,
            'reviewer_id': self.reviewer_id,
            'reviewer_name': self.reviewer.name if self.reviewer else None,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
