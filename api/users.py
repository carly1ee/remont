from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import logging

from dal.users import UserDAL
from dal.request import RequestDAL
from dal.balance_history import BalanceHistoryDAL
from dal.request_history import RequestHistoryDAL
from dal.engineer_profile import EngineerProfileDAL


# Создание блюпринта
users_bp = Blueprint('users', __name__, url_prefix='/users')
logger = logging.getLogger(__name__)


@users_bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    try:
        # Проверяем, что запрос делает администратор
        current_user_id = get_jwt_identity()
        admin = UserDAL.get_user_by_id(current_user_id)
        if not admin or admin.get('role_id') != 3:  # 3 - ID роли администратора
            return jsonify({'error': 'Only admin can register users'}), 403

        data = request.get_json()
        required_fields = ['name', 'login', 'password', 'role_id']

        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        if data['role_id'] == 1 and 'schedule' not in data:
            return jsonify({'error': 'Schedule is required for engineers'}), 400

        # Проверяем, что назначаемая роль существует
        if not UserDAL.check_role_exists(data['role_id']):
            return jsonify({'error': 'Invalid role_id'}), 400

        # Создание пользователя
        result = UserDAL.create_user(
            name=data['name'],
            login=data['login'],
            password=data['password'],
            role_id=data['role_id'],
            phone=data.get('phone'),
            email=data.get('email')
        )

        if data['role_id'] == 1:
            UserDAL.create_engineer_profile(user_id=result, schedule=data.get('schedule'))
            logger.info(f"Engineer profile created for user {result}")

        return jsonify({
            'message': 'User created successfully',
            'user_id': result
        }), 201

    except ValueError as e:
        if str(e) == "Login already exists":
            return jsonify({'error': 'Login already exists'}), 409
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@users_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or 'login' not in data or 'password' not in data:
            return jsonify({'error': 'Missing login or password'}), 400

        user = UserDAL.authenticate_user(data['login'], data['password'])
        if user:
            access_token = create_access_token(identity=str(user['user_id']))
            return jsonify({
                'access_token': access_token,
                'user': {
                    'user_id': user['user_id'],
                    'name': user['name'],
                    'role': user['role'],
                    'phone': user['phone'],
                    'email': user['email']
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

        response = {
            'user_id': user['user_id'],
            'name': user['name'],
            'role': user['role'],
            'phone': user['phone'],
            'email': user['email']
        }

        if user['role_id'] == 1:
            engineer_profile = UserDAL.get_engineer_profile(user_id)
            if engineer_profile:
                response.update({
                    'balance': engineer_profile['balance'],
                    'schedule': engineer_profile['schedule']
                })

        return jsonify(response), 200

        return jsonify({'error': 'User not found'}), 404

    except Exception as e:
        logger.error(f"Profile error: {e}")
        return jsonify({'error': 'Internal server error'}), 500



@users_bp.route('/<int:user_id>', methods=['PATCH'])
@jwt_required()
def update_user(user_id):
    try:
        # Получаем текущего пользователя
        current_user_id = get_jwt_identity()
        current_user = UserDAL.get_user_by_id(current_user_id)
        if not current_user:
            return jsonify({'error': 'Неавторизованный доступ'}), 401

        # Получаем целевого пользователя
        target_user = UserDAL.get_user_by_id(user_id)
        if not target_user:
            return jsonify({'error': 'Пользователь не найден'}), 404

        # Проверка прав (админ или сам пользователь)
        if current_user['role_id'] != 3:
            return jsonify({'error': 'Недостаточно прав'}), 403

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Нет данных для обновления'}), 400

        # Разрешенные поля для обновления
        allowed_fields = {'name', 'phone', 'email', 'password', 'login', 'role_id'}

        # Фильтрация данных
        update_data = {
            k: v for k, v in data.items()
            if k in allowed_fields and v is not None
        }

        if not update_data:
            return jsonify({'error': 'Нет допустимых полей для обновления'}), 400

        # Обновление данных
        if UserDAL.update_user(user_id, **update_data):
            updated_user = UserDAL.get_user_by_id(user_id)
            return jsonify({
                'message': 'Данные обновлены',
                'user': {
                    'id': updated_user['user_id'],
                    'login': updated_user['login'],
                    'name': updated_user['name'],
                    'email': updated_user['email'],
                    'phone': updated_user['phone'],
                    'role_id': updated_user['role_id']
                }
            }), 200

        return jsonify({'error': 'Ошибка при обновлении'}), 500

    except Exception as e:
        logger.error(f"Error updating user ID {user_id}: {str(e)}")
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500


@users_bp.route('/<int:user_id>/schedule', methods=['PATCH'])
@jwt_required()
def update_schedule(user_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = UserDAL.get_user_by_id(current_user_id)
        target_user = UserDAL.get_user_by_id(user_id)

        # Проверка прав (админ или сам пользователь)
        if current_user['role_id'] != 3:
            return jsonify({'error': 'Insufficient permissions'}), 403

        # Проверка что пользователь - инженер
        if target_user['role_id'] != 1:
            return jsonify({'error': 'User is not an engineer'}), 400

        schedule = request.json.get('schedule')
        if not schedule:
            return jsonify({'error': 'Schedule not provided'}), 400

        if UserDAL.update_engineer_schedule(user_id, schedule):
            return jsonify({'message': 'Schedule updated'}), 200

        return jsonify({'error': 'Failed to update schedule'}), 500

    except Exception as e:
        logger.error(f"Error updating schedule: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@users_bp.route('/<int:user_id>/credentials', methods=['GET'])
@jwt_required()
def get_user_credentials(user_id: int):
    try:
        current_user_id = get_jwt_identity()
        user = UserDAL.get_user_by_id(current_user_id)

        # Проверяем, что текущий пользователь — менеджер с user_id = 3
        if not user or user['role_id'] != 3:
            return jsonify({'error': 'Access denied'}), 403

        # Получаем данные пользователя
        credentials = UserDAL.get_user_login_and_password_by_id(user_id)

        if isinstance(credentials, str):
            if credentials == "User not found":
                return jsonify({'error': 'User not found'}), 404
            return jsonify({'error': credentials}), 500

        return jsonify({
            'user_id': user_id,
            'login': credentials['login'],
            'password': credentials['passw']
        }), 200

    except Exception as e:
        logger.error(f"Error fetching user credentials: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id: int):
    try:
        current_user_id = get_jwt_identity()
        current_user = UserDAL.get_user_by_id(current_user_id)
        # Только админ (role_id=3) может удалять пользователей
        if not current_user or current_user['role_id'] != 3 or int(current_user_id) == user_id:
            return jsonify({'error': 'Access denied'}), 403

        # Получаем данные удаляемого пользователя
        target_user = UserDAL.get_user_by_id(user_id)
        if not target_user:
            return jsonify({'error': 'User not found'}), 404

        role_id = target_user['role_id']

        # Обнуляем все ссылки на пользователя
        RequestDAL.nullify_engineer_id_in_requests(user_id)
        RequestDAL.nullify_operator_id_in_requests(user_id)
        RequestHistoryDAL.nullify_changer_id_in_request_history(user_id)

        # Если пользователь — инженер
        if role_id == 1:
            BalanceHistoryDAL.delete_balance_history_by_engineer(user_id)
            EngineerProfileDAL.delete_engineer_profile(user_id)

        # Если пользователь — менеджер
        elif role_id == 2:
            BalanceHistoryDAL.nullify_admin_id_in_balance_history(user_id)

        # Удаляем самого пользователя
        UserDAL.delete_user(user_id)

        return jsonify({
            'message': 'User deleted successfully',
            'user_id': user_id
        }), 200

    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@users_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_users():
    try:
        current_user_id = get_jwt_identity()
        current_user = UserDAL.get_user_by_id(current_user_id)

        # Проверяем, что текущий пользователь — менеджер или админ
        if not current_user or current_user['role_id'] != 3:
            return jsonify({'error': 'Access denied'}), 403

        # Получаем всех пользователей
        users = UserDAL.get_all_users_with_details()

        if isinstance(users, str):
            return jsonify({'error': users}), 500

        # Формируем ответ
        response = []
        for user in users:
            user_data = {
                "user_id": user["user_id"],
                "name": user["name"],
                "phone": user["phone"],
                "email": user["email"],
                "role_id": user["role_id"],
                "role": user["role"]
            }

            # Если это инженер — добавляем schedule и balance
            if user["role_id"] == 1:
                user_data.update({
                    "schedule": user.get("schedule"),
                    "balance": float(user["balance"]) if user.get("balance") is not None else 0.0
                })

            response.append(user_data)

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return jsonify({'error': 'Internal server error'}), 500