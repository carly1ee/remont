from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from dal.request import RequestDAL
from dal.users import UserDAL
import logging
from datetime import datetime

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

        required_fields = ['status_id', 'phone', 'address', 'techniq', 'description', 'customer_name']
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
            customer_name=data['customer_name'],
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


@requests_bp.route('/engineer', methods=['GET'])
@jwt_required()
def my_requests():
    try:
        current_user_id = get_jwt_identity()
        user = UserDAL.get_user_by_id(current_user_id)

        if not user or user.get('role_id') != 1:
            return jsonify({'error': 'Only engineers can access their requests'}), 403

        # Получаем дату из запроса
        date_str = request.args.get('date')
        if not date_str:
            return jsonify({'error': 'Missing date parameter (format: YYYY-MM-DD)'}), 400

        try:
            # Проверяем формат даты
            date_filter = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        # Фильтруем по status_id = 2 и 3
        requests = RequestDAL.get_requests_by_engineer(
            engineer_id=current_user_id,
            status_ids=[2, 3],
            date_filter=date_filter
        )

        if isinstance(requests, str):  # Ошибка
            return jsonify({'error': requests}), 500

        return jsonify({
            "engineer_id": current_user_id,
            "total": len(requests),
            "date_filter": date_str,
            "requests": requests
        }), 200

    except Exception as e:
        logger.error(f"Error fetching requests: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@requests_bp.route('/engineer/completed/<int:page>', methods=['GET'])
@jwt_required()
def my_completed_requests(page: int):
    try:
        current_user_id = get_jwt_identity()
        user = UserDAL.get_user_by_id(current_user_id)

        if not user or user.get('role_id') != 1:  # Только инженер
            return jsonify({'error': 'Only engineers can access their requests'}), 403

        per_page = 10

        # Получаем заявки
        requests = RequestDAL.get_completed_requests(current_user_id, page, per_page)

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
        logger.error(f"Error fetching completed requests: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@requests_bp.route('/engineer/<int:request_id>', methods=['PUT'])
@jwt_required()
def update_request(request_id: int):
    try:
        current_user_id = get_jwt_identity()
        user = UserDAL.get_user_by_id(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        result = RequestDAL.update_request(
            user_id=current_user_id,
            role_id=user['role_id'],
            request_id=request_id,
            updates=data
        )

        if isinstance(result, str):  # Ошибка
            return jsonify({'error': result}), 500

        return jsonify({
            'message': 'Request updated successfully',
            'request': result
        }), 200

    except Exception as e:
        logger.error(f"Error updating request: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@requests_bp.route('/completed', methods=['GET'])
@jwt_required()
def get_completed_requests():
    try:
        current_user_id = get_jwt_identity()
        user = UserDAL.get_user_by_id(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        role_id = user['role_id']

        # Получаем даты из параметров запроса
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        if not start_date_str or not end_date_str:
            return jsonify({'error': 'Missing start_date or end_date'}), 400

        try:
            start_date = datetime.fromisoformat(start_date_str)
            end_date = datetime.fromisoformat(end_date_str)
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400

        if role_id == 1:  # Инженер — только свои заявки
            count = RequestDAL.count_completed_requests(current_user_id, start_date, end_date)

            if isinstance(count, str):
                return jsonify({'error': count}), 500

            return jsonify({
                'engineer_id': current_user_id,
                'engineer_name': user['name'],
                'total_completed': count,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            }), 200

        elif role_id == 3:  # Менеджер — все инженеры
            engineer_list = RequestDAL.count_all_engineers_completed_requests(start_date, end_date)

            if isinstance(engineer_list, str):
                return jsonify({'error': engineer_list}), 500

            return jsonify({
                'manager_id': current_user_id,
                'manager_name': user['name'],
                'reports': engineer_list,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            }), 200

        else:
            return jsonify({'error': 'Access denied'}), 403

    except Exception as e:
        logger.error(f"Error fetching completed requests: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@requests_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_current_month_request_stats():
    try:
        current_user_id = get_jwt_identity()
        user = UserDAL.get_user_by_id(current_user_id)

        if not user or user['role_id'] not in [1, 2]:  # только оператор или менеджер
            return jsonify({'error': 'Access denied'}), 403

        # Получаем статистику за текущий месяц
        stats = RequestDAL.get_request_stats_this_month()

        if isinstance(stats, str):
            return jsonify({'error': stats}), 500

        return jsonify({
            'request_stats': {
                'total_created': stats['total_created'],
                'total_assigned': stats['total_assigned'],
                'total_in_works': stats['total_in_works'],
                'total_done': stats['total_done']
            },
            'period': {
                'start_date': stats['period']['start_date'],
                'end_date': stats['period']['end_date']
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching current month request statistics: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@requests_bp.route('/filter', methods=['POST'])
@jwt_required()
def filter_requests():
    try:
        current_user_id = get_jwt_identity()
        user = UserDAL.get_user_by_id(current_user_id)

        if not user or user['role_id'] not in [2, 3]:  # менеджер или оператор
            return jsonify({'error': 'Access denied'}), 403

        data = request.get_json()

        # Парсим параметры из JSON
        engineer_id = data.get('engineer_id')
        status_ids = data.get('status_ids')  # Ожидаем список чисел
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        page = data.get('page', 1)
        per_page = data.get('per_page', 10)

        # Конвертируем даты
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None

        # Проверяем типы
        if not isinstance(page, int) or page < 1:
            page = 1
        if not isinstance(per_page, int) or per_page < 1 or per_page > 100:
            per_page = 10

        # Получаем данные из БД
        result = RequestDAL.get_filtered_requests(
            engineer_id=engineer_id,
            status_ids=status_ids,
            start_date=start_date,
            end_date=end_date,
            page=page,
            per_page=per_page
        )

        if isinstance(result, str):
            return jsonify({'error': result}), 500

        return jsonify({
            'manager_name': user['name'],
            'filters': {
                'engineer_id': engineer_id,
                'status_ids': status_ids or list(range(1, 5)),
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'page': page,
                'per_page': per_page
            },
            'total': len(result),
            'requests': result
        }), 200

    except Exception as e:
        logger.error(f"Error filtering requests: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@requests_bp.route('/engineers/stats', methods=['POST'])
@jwt_required()
def get_engineers_stats():
    try:
        current_user_id = get_jwt_identity()
        user = UserDAL.get_user_by_id(current_user_id)

        if not user or user['role_id'] != 3:  # менеджер или оператор
            return jsonify({'error': 'Access denied'}), 403

        data = request.get_json(silent=True)
        if data is None:
            data = {}

        # Пагинация
        page = data.get('page', 1)
        per_page = data.get('per_page', 10)

        if not isinstance(page, int) or page < 1:
            page = 1
        if not isinstance(per_page, int) or per_page < 1 or per_page > 100:
            per_page = 10

        # Получаем данные из БД
        result = RequestDAL.get_engineers_stats_with_balance_and_requests()

        if isinstance(result, str):
            return jsonify({'error': result}), 500

        total = len(result)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_result = result[start:end]

        return jsonify({
            'manager_name': user['name'],
            'period': {
                'start_date': datetime(datetime.today().year, datetime.today().month, 1).isoformat(),
                'end_date': datetime.now().isoformat()
            },
            'filters': {
                'page': page,
                'per_page': per_page
            },
            'total': total,
            'engineers': paginated_result
        }), 200

    except Exception as e:
        logger.error(f"Error fetching engineers statistics: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@requests_bp.route('/delete/<int:request_id>', methods=['PUT'])
@jwt_required()
def soft_delete_request(request_id: int):
    try:
        current_user_id = get_jwt_identity()
        user = UserDAL.get_user_by_id(current_user_id)

        if not user or user['role_id'] not in [2, 3]:  # Только оператор или менеджер
            return jsonify({'error': 'Access denied'}), 403

        # Обновляем статус заявки
        result = RequestDAL.update_request(
            user_id=current_user_id,
            role_id=user['role_id'],
            request_id=request_id,
            updates={'status_id': 5}  # status_id = 5 → deleted
        )

        if isinstance(result, str):  # Ошибка
            return jsonify({'error': result}), 500

        return jsonify({
            'message': 'Request marked as deleted successfully',
            'request_id': request_id,
            'new_status': 'deleted'
        }), 200

    except Exception as e:
        logger.error(f"Error deleting request: {e}")
        return jsonify({'error': 'Internal server error'}), 500