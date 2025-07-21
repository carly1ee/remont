from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from dal.request_history import RequestHistoryDAL
from dal.users import UserDAL
import logging

logger = logging.getLogger(__name__)

history_bp = Blueprint('request_history', __name__, url_prefix='/requests/history')

@history_bp.route('/<int:request_id>', methods=['GET'])
@jwt_required()
def get_history(request_id: int):
    try:
        current_user_id = get_jwt_identity()
        user = UserDAL.get_user_by_id(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        history = RequestHistoryDAL.get_request_history(request_id)

        return jsonify({
            'request_id': request_id,
            'history': history
        }), 200

    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        return jsonify({'error': 'Internal server error'}), 500