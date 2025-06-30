from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from dal.users import UserDAL
import logging

# Создание блюпринта
users_bp = Blueprint('users', __name__, url_prefix='/users')
logger = logging.getLogger(__name__)


@users_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        required_fields = ['name', 'login', 'password', 'role_id']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        result = UserDAL.create_user(
            name=data['name'],
            login=data['login'],
            password=data['password'],
            role_id=data['role_id']
        )

        if isinstance(result, int):
            return jsonify({'message': 'User created', 'user_id': result}), 201
        return jsonify({'error': result}), 400

    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@users_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or 'login' not in data or 'password' not in data:
            return jsonify({'error': 'Missing login or password'}), 400

        user = UserDAL.authenticate_user(data['login'], data['password'])  # Исправлено name -> login
        if user:
            access_token = create_access_token(identity=user['user_id'])
            return jsonify({
                'access_token': access_token,
                'user': {
                    'name': user['name'],
                    'role': user['role']
                }
            }), 200

        return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    try:
        current_user_id = get_jwt_identity()
        user = UserDAL.get_user_by_id(current_user_id)

        if user:
            return jsonify({
                'name': user['name'],
                'role': user['role']
            }), 200

        return jsonify({'error': 'User not found'}), 404

    except Exception as e:
        logger.error(f"Profile error: {e}")
        return jsonify({'error': 'Internal server error'}), 500