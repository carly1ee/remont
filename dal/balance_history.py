# dal/balance.py

from typing import List, Union
from db_manager import DatabaseManager
import logging

logger = logging.getLogger(__name__)

class BalanceHistoryDAL:
    @staticmethod
    def get_balance_history(engineer_id: int) -> Union[List[dict], str]:
        """
        Получает историю изменений баланса для конкретного инженера
        """
        try:
            with DatabaseManager.get_cursor() as cursor:
                query = """
                    SELECT 
                        bh.bh_id,
                        bh.admin_id,
                        bh.engineer_id,
                        bh.old_sum,
                        bh.new_sum,
                        bh.changed_at
                    FROM balance_history bh
                    WHERE bh.engineer_id = %s
                    ORDER BY bh.changed_at DESC;
                """
                cursor.execute(query, (engineer_id,))
                result = cursor.fetchall()
                return result if result else []
        except Exception as e:
            logger.error(f"Error fetching balance history for engineer {engineer_id}: {e}")
            return "Internal server error"