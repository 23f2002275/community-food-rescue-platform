from uuid import uuid4
from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user, hash_password
from flask_security.utils import verify_and_update_password
from extensions import db
from security_setup import user_datastore

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))
    name = str(data.get('name', '')).strip()
    role = str(data.get('role', '')).strip().lower()

    if not email or not password or not name or not role:
        return jsonify({'message': 'All fields are required'}), 400

    if role not in ['donor', 'receiver']:
        return jsonify({'message': 'Role must be donor or receiver'}), 400

    if len(password) < 6:
        return jsonify({'message': 'Password must contain at least 6 characters'}), 400

    if user_datastore.find_user(email=email):
        return jsonify({'message': 'Email already registered'}), 409

    user = user_datastore.create_user(
        email=email,
        password=hash_password(password),
        name=name,
        phone=str(data.get('phone', '')).strip(),
        address=str(data.get('address', '')).strip(),
        roles=[role],
        fs_uniquifier=uuid4().hex,
    )
    db.session.commit()

    return jsonify({'message': 'Registration successful', 'user': user.to_dict()}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user = user_datastore.find_user(email=email)

    if not user or not verify_and_update_password(password, user):
        return jsonify({'message': 'Invalid email or password'}), 401

    if not user.active:
        return jsonify({'message': 'Account is blocked'}), 403

    db.session.commit()

    return jsonify({
        'message': 'Login successful',
        'token': user.get_auth_token(),
        'user': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@auth_required('token')
def me():
    return jsonify(current_user.to_dict()), 200

@auth_bp.route('/profile', methods=['PUT'])
@auth_required('token')
def update_profile():
    data = request.get_json() or {}
    name = str(data.get('name', '')).strip()

    if not name:
        return jsonify({'message': 'Name is required'}), 400

    current_user.name = name
    current_user.phone = str(data.get('phone', '')).strip()
    current_user.address = str(data.get('address', '')).strip()
    db.session.commit()

    return jsonify({'message': 'Profile updated', 'user': current_user.to_dict()}), 200

@auth_bp.route('/logout', methods=['POST'])
@auth_required('token')
def logout():
    user_datastore.set_token_uniquifier(current_user, uuid4().hex)
    db.session.commit()
    return jsonify({'message': 'Logged out'}), 200
