from typing import Optional, Dict
import logging
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class EngineerProfileDAL:
    @staticmethod
    def create_profile(user_id: int, schedule: str = None) -> int:
        """Создает профиль инженера с балансом 0"""
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
    def get_profile(user_id: int) -> Optional[Dict]:
        """Получает профиль инженера"""
        try:
            with DatabaseManager.get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT engin_id, user_id, balance, schedule
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
    def update_schedule(user_id: int, schedule: str) -> bool:
        """Обновляет только расписание инженера"""
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