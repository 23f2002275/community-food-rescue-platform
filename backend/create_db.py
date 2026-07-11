from datetime import datetime, timedelta
from uuid import uuid4
from flask_security import hash_password
from app import create_app
from extensions import db
from security_setup import user_datastore
from models import FoodListing

app = create_app()

with app.app_context():
    db.create_all()

    for role_name in ['admin', 'donor', 'receiver']:
        if not user_datastore.find_role(role_name):
            user_datastore.create_role(name=role_name)

    users = [
        ('admin@foodrescue.com', 'Admin User', 'admin', 'admin123'),
        ('donor@foodrescue.com', 'Demo Donor', 'donor', 'donor123'),
        ('receiver@foodrescue.com', 'Demo Receiver', 'receiver', 'receiver123')
    ]

    for email, name, role, password in users:
        if not user_datastore.find_user(email=email):
            user_datastore.create_user(
                email=email,
                name=name,
                password=hash_password(password),
                roles=[role],
                fs_uniquifier=uuid4().hex,
            )

    db.session.commit()

    donor = user_datastore.find_user(email='donor@foodrescue.com')

    if FoodListing.query.count() == 0:
        listings = [
            FoodListing(
                donor_id=donor.id,
                title='Fresh vegetable meals',
                description='Packed meals prepared this afternoon.',
                food_type='Cooked Food',
                dietary_tag='Vegetarian',
                total_quantity=20,
                available_quantity=20,
                unit='plates',
                pickup_location='Taramani, Chennai',
                pickup_notes='Bring your own carry bags.',
                expiry_time=datetime.utcnow() + timedelta(hours=8),
                status='ACTIVE'
            ),
            FoodListing(
                donor_id=donor.id,
                title='Bread and bakery items',
                description='Unsold sealed bakery products.',
                food_type='Bakery',
                dietary_tag='Vegetarian',
                total_quantity=15,
                available_quantity=15,
                unit='packs',
                pickup_location='Velachery, Chennai',
                pickup_notes='Pickup before closing time.',
                expiry_time=datetime.utcnow() + timedelta(hours=18),
                status='ACTIVE'
            )
        ]
        db.session.add_all(listings)
        db.session.commit()

    print('Database created')
    print('admin@foodrescue.com / admin123')
    print('donor@foodrescue.com / donor123')
    print('receiver@foodrescue.com / receiver123')
