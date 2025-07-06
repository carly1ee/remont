from typing import Optional, Dict, Union
import logging
from db_manager import DatabaseManager

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

    @staticmethod
    def update_engineer_balance(admin_id: int, engineer_id: int, new_balance: float) -> Union[str, dict]:
        """
        Обновляет баланс инженера. Менять может только пользователь с ролью менеджера (role_id = 3)
        """

        try:
            with DatabaseManager.get_cursor() as cursor:
                # Проверяем, является ли пользователь менеджером
                cursor.execute("""
                        SELECT 1 FROM users WHERE user_id = %s AND role_id = 3;
                    """, (admin_id,))
                is_admin = cursor.fetchone()

                if not is_admin:
                    return "Only manager can change engineer's balance"

                # Получаем текущий баланс
                cursor.execute("""
                        SELECT balance FROM engineer_profile WHERE user_id = %s;
                    """, (engineer_id,))
                result = cursor.fetchone()

                if not result:
                    return "Engineer profile not found"

                old_balance = result['balance']

                # Обновляем баланс
                cursor.execute("""
                        UPDATE engineer_profile
                        SET balance = %s
                        WHERE user_id = %s
                        RETURNING balance;
                    """, (new_balance, engineer_id))

                # Логируем изменение
                cursor.execute("""
                        INSERT INTO balance_history (
                            admin_id, engineer_id, old_sum, new_sum
                        ) VALUES (%s, %s, %s, %s);
                    """, (admin_id, engineer_id, old_balance, new_balance))

                logger.info(f"Balance updated for engineer {engineer_id} by admin {admin_id}")

                return {
                    "message": "Balance updated successfully",
                    "old_balance": old_balance,
                    "new_balance": new_balance
                }

        except Exception as e:
            logger.error(f"Error updating engineer balance: {e}")
            return "Internal server error"

    @staticmethod
    def get_engineer_balance(engineer_user_id: int) -> Union[Dict[str, Union[int, float]], str]:
        """
        Получает баланс инженера по его user_id
        """
        try:
            with DatabaseManager.get_cursor() as cursor:
                query = """
                        SELECT 
                            ep.balance,
                            u.name AS engineer_name
                        FROM engineer_profile ep
                        JOIN users u ON ep.user_id = u.user_id
                        WHERE ep.user_id = %s;
                    """
                cursor.execute(query, (engineer_user_id,))
                result = cursor.fetchone()

                if not result:
                    logger.warning(f"Engineer with ID {engineer_user_id} not found")
                    return "Engineer not found"

                return {
                    'engineer_id': engineer_user_id,
                    'engineer_name': result['engineer_name'],
                    'balance': float(result['balance']) if result['balance'] else 0.0
                }

        except Exception as e:
            logger.error(f"Error fetching balance for engineer {engineer_user_id}: {e}")
            return "Internal server error"