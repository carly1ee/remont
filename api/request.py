from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from dal.request import RequestDAL
from dal.users import UserDAL
import logging

# Создание блюпринта
requests_bp = Blueprint('requests', __name__, url_prefix='/requests')
logger = logging.getLogger(__name__)


@requests_bp.route('/', methods=['POST'])
@jwt_required()
def create_request():
    try:
        current_user_id = get_jwt_identity()
        user = UserDAL.get_user_by_id(current_user_id)

        if not user or user.get('role_id') != 2:  # Только оператор (role_id=2)
            return jsonify({'error': 'Only operator can create requests'}), 403

        data = request.get_json()

        required_fields = ['status_id', 'phone', 'address', 'techniq', 'description']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        engineer_id = data.get('engineer_id')  # Необязательное поле

        result = RequestDAL.create_request(
            operator_id=current_user_id,
            status_id=data['status_id'],
            phone=data['phone'],
            address=data['address'],
            techniq=data['techniq'],
            description=data['description'],
            engineer_id=engineer_id
        )

        if isinstance(result, dict):
            response = {
                'message': 'Request created successfully',
                'request_id': result['request_id'],
                'creation_date': result['creation_date']
            }
            if engineer_id:
                response['assigned_time'] = result['assigned_time']

            return jsonify(response), 201

        return jsonify({'error': result}), 400

    except Exception as e:
        logger.error(f"Request creation error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@requests_bp.route('/engineer/<int:page>', methods=['GET'])
@jwt_required()
def my_requests_paginated(page: int):
    try:
        current_user_id = get_jwt_identity()
        user = UserDAL.get_user_by_id(current_user_id)

        if not user or user.get('role_id') != 1:
            return jsonify({'error': 'Only engineers can access their requests'}), 403

        per_page = 10
        requests = RequestDAL.get_requests_by_engineer(current_user_id, page, per_page)

        if isinstance(requests, str):  # Ошибка
            return jsonify({'error': requests}), 500

        return jsonify({
            "engineer_id": current_user_id,
            "page": page,
            "per_page": per_page,
            "total": len(requests),
            "requests": requests
        }), 200

    except Exception as e:
        logger.error(f"Error fetching requests: {e}")
        return jsonify({'error': 'Internal server error'}), 500