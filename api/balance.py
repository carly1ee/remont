from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from dal.engineer_profile import EngineerProfileDAL
from dal.users import UserDAL
import logging

logger = logging.getLogger(__name__)

balance_bp = Blueprint('balance', __name__, url_prefix='/balance')

@balance_bp.route('/<int:engineer_id>', methods=['PUT'])
@jwt_required()
def update_balance(engineer_id: int):
    try:
        current_user_id = get_jwt_identity()
        user = UserDAL.get_user_by_id(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()
        if 'new_balance' not in data:
            return jsonify({'error': 'Missing field: new_balance'}), 400

        result = EngineerProfileDAL.update_engineer_balance(
            admin_id=current_user_id,
            engineer_id=engineer_id,
            new_balance=data['new_balance']
        )

        if isinstance(result, str):  # Ошибка
            return jsonify({'error': result}), 400 if result == "Only manager can change engineer's balance" else 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error updating balance: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@balance_bp.route('/<int:engineer_id>', methods=['GET'])
@jwt_required()
def get_engineer_balance(engineer_id: int):
    try:
        current_user_id = get_jwt_identity()
        user = UserDAL.get_user_by_id(current_user_id)

        # Проверяем, что пользователь — инженер или менеджер
        if not user or user.get('role_id') not in [1, 3]:  # 1 = engineer, 3 = manager
            return jsonify({'error': 'Access denied'}), 403
        # Если текущий пользователь не админ, он может запросить только свой баланс
        if user['role_id'] == 1 and int(current_user_id) != engineer_id:
            return jsonify({'error': 'You can only view your own balance'}), 403

        # Получаем баланс из DAL
        balance_info = EngineerProfileDAL.get_engineer_balance(engineer_id)

        if isinstance(balance_info, str):
            return jsonify({'error': balance_info}), 404 if balance_info == "Engineer not found" else 500

        return jsonify(balance_info), 200

    except Exception as e:
        logger.error(f"Error fetching engineer balance: {e}")
        return jsonify({'error': 'Internal server error'}), 500