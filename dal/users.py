from typing import Optional, Dict, Union
import logging
from datetime import datetime
from db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class UserDAL:
    @staticmethod
    def create_user(name: str, login: str, password: str, role_id: int = 1,
                  phone: Optional[str] = None, email: Optional[str] = None) -> Union[int, str]:
        try:
            with DatabaseManager.get_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (role_id, name, login, passw, phone, email)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING user_id;
                    """,
                    (role_id, name, login, password, phone, email)
                )
                user_id = cursor.fetchone()['user_id']
                logger.info(f"User {login} created with ID {user_id}")
                return user_id
        except psycopg2.IntegrityError as e:
            if 'login' in str(e):
                return "Login already exists"
            logger.error(f"Integrity error: {e}")
            return "User creation error"
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return "Internal server error"

    @staticmethod
    def authenticate_user(login: str, password: str) -> Optional[Dict]:
        try:
            with DatabaseManager.get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 
                        u.user_id, 
                        u.name,
                        u.phone,
                        u.email,
                        r.role
                    FROM users u
                    JOIN roles r ON u.role_id = r.role_id
                    WHERE u.login = %s AND u.passw = %s;
                    """,
                    (login, password)
                )
                user = cursor.fetchone()

                if user:
                    logger.info(f"User {login} authenticated successfully")
                    return dict(user)

                logger.warning(f"Authentication failed for {login}")
                return None

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict]:
        """Получение пользователя по ID"""
        try:
            with DatabaseManager.get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 
                        u.user_id, 
                        u.name,
                        u.login,
                        u.phone,
                        u.email,
                        r.role,
                        r.role_id
                    FROM users u
                    JOIN roles r ON u.role_id = r.role_id
                    WHERE u.user_id = %s;
                    """,
                    (user_id,)
                )
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    @staticmethod
    def check_role_exists(role_id: int) -> bool:
        """Проверяет существование роли"""
        try:
            with DatabaseManager.get_cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM roles WHERE role_id = %s;",
                    (role_id,)
                )
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking role: {e}")
            return False

    @staticmethod
    def delete_user_by_id(user_id: int) -> bool:
        """Удаляет пользователя по ID"""
        try:
            with DatabaseManager.get_cursor() as cursor:
                cursor.execute(
                    "DELETE FROM users WHERE user_id = %s RETURNING user_id;",
                    (user_id,)
                )
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error deleting user ID {user_id}: {e}")
            return False

    @staticmethod
    def user_exists_by_id(user_id: int) -> bool:
        """Проверяет существование пользователя по ID"""
        try:
            with DatabaseManager.get_cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM users WHERE user_id = %s;",
                    (user_id,)
                )
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking user existence ID {user_id}: {e}")
            return False

    @staticmethod
    def update_user(user_id: int, **fields) -> bool:
        """Обновляет данные пользователя по ID"""
        try:
            if not fields:
                return False

            with DatabaseManager.get_cursor() as cursor:
                set_clause = ", ".join([f"{field} = %s" for field in fields])
                query = f"""
                    UPDATE users
                    SET {set_clause}
                    WHERE user_id = %s
                    RETURNING user_id;
                """
                params = list(fields.values()) + [user_id]

                cursor.execute(query, params)
                return cursor.fetchone() is not None

        except Exception as e:
            logger.error(f"Error updating user ID {user_id}: {e}")
            return False

    @staticmethod
    def create_engineer_profile(user_id: int, schedule: str = None) -> int:
        """Создает профиль инженера"""
        try:
            with DatabaseManager.get_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO engineer_profile (user_id, balance, schedule)
                    VALUES (%s, 0, %s)
                    RETURNING engin_id;
                    """,
                    (user_id, schedule)
                )
                return cursor.fetchone()['engin_id']
        except Exception as e:
            logger.error(f"Error creating engineer profile: {e}")
            raise

    @staticmethod
    def get_engineer_profile(user_id: int) -> Optional[Dict]:
        """Получает профиль инженера"""
        try:
            with DatabaseManager.get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT balance, schedule
                    FROM engineer_profile
                    WHERE user_id = %s;
                    """,
                    (user_id,)
                )
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting engineer profile: {e}")
            return None

    @staticmethod
    def update_engineer_schedule(user_id: int, schedule: str) -> bool:
        """Обновляет расписание инженера"""
        try:
            with DatabaseManager.get_cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE engineer_profile
                    SET schedule = %s
                    WHERE user_id = %s
                    RETURNING engin_id;
                    """,
                    (schedule, user_id)
                )
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error updating engineer schedule: {e}")
            return False

