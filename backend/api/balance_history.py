# api/balance_history.py

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from dal.balance_history import BalanceHistoryDAL
from dal.users import UserDAL
import logging

logger = logging.getLogger(__name__)

balance_history_bp = Blueprint('balance_history', __name__, url_prefix='/balance/history')


@balance_history_bp.route('/<int:engineer_id>', methods=['GET'])
@jwt_required()
def get_engineer_balance_history(engineer_id: int):
    try:
        current_user_id = get_jwt_identity()
        user = UserDAL.get_user_by_id(current_user_id)

        # Проверяем, что пользователь — менеджер или администратор
        if not user or user['role_id'] != 3:  # например, role_id=2 — менеджер, 3 — админ
            return jsonify({'error': 'Access denied'}), 403

        # Получаем историю баланса
        history = BalanceHistoryDAL.get_balance_history(engineer_id)

        if isinstance(history, str):  # ошибка
            return jsonify({'error': history}), 500

        if not history:  # пустая история
            return jsonify({
                'message': 'No balance history found for this engineer',
                'history': []
            }), 200

        return jsonify({
            'engineer_id': engineer_id,
            'history': history
        }), 200

    except Exception as e:
        logger.error(f"Error fetching balance history: {e}")
        return jsonify({'error': 'Internal server error'}), 500