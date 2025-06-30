from typing import Optional, Dict, Union
import logging
from datetime import datetime
from db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class UserDAL:
    @staticmethod
    def create_user(name: str, login: str, password: str, role_id: int = 1) -> Union[int, str]:
        try:
            with DatabaseManager.get_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (role_id, name, login, passw)
                    VALUES (%s, %s, %s, %s)
                    RETURNING user_id;
                    """,
                    (role_id, name, login, password)
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
                        r.role
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