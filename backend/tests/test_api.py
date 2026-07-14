from uuid import uuid4
import pytest
from flask_security import hash_password
from app import create_app
from extensions import db
from security_setup import user_datastore

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite://',
        'WTF_CSRF_ENABLED': False
    })

    with app.app_context():
        db.create_all()
        for role in ['admin', 'donor', 'receiver']:
            user_datastore.create_role(name=role)
        user_datastore.create_user(
            email='donor@test.com',
            name='Donor',
            password=hash_password('password'),
            roles=['donor'],
            fs_uniquifier=uuid4().hex,
        )
        user_datastore.create_user(
            email='receiver@test.com',
            name='Receiver',
            password=hash_password('password'),
            roles=['receiver'],
            fs_uniquifier=uuid4().hex,
        )
        db.session.commit()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def login(client, email):
    response = client.post('/api/auth/login', json={'email': email, 'password': 'password'})
    return response.get_json()['token']

def test_invalid_login(client):
    response = client.post('/api/auth/login', json={'email': 'donor@test.com', 'password': 'wrong'})
    assert response.status_code == 401

def test_protected_endpoint_without_token(client):
    response = client.get('/api/auth/me')
    assert response.status_code == 401

def test_receiver_cannot_create_listing(client):
    token = login(client, 'receiver@test.com')
    response = client.post('/api/listings', headers={'Authentication-Token': token}, json={})
    assert response.status_code == 403

def test_donor_can_create_listing(client):
    token = login(client, 'donor@test.com')
    response = client.post('/api/listings', headers={'Authentication-Token': token}, json={
        'title': 'Test food',
        'food_type': 'Cooked Food',
        'total_quantity': 10,
        'unit': 'plates',
        'pickup_location': 'Chennai',
        'expiry_time': '2099-01-01T10:00:00',
        'status': 'ACTIVE'
    })
    assert response.status_code == 201
    assert response.get_json()['listing']['available_quantity'] == 10
