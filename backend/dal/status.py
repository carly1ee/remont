from typing import Union, Dict
from db_manager import DatabaseManager
import logging

logger = logging.getLogger(__name__)


class StatusDAL:
    @staticmethod
    def get_status_by_id(status_id: int) -> Union[Dict, str]:
        """
        Получает статус по ID
        """
        try:
            with DatabaseManager.get_cursor() as cursor:
                cursor.execute("""
                    SELECT status FROM status WHERE status_id = %s;
                """, (status_id,))
                result = cursor.fetchone()
                if not result:
                    return None
                return dict(result)
        except Exception as e:
            logger.error(f"Error fetching status by ID {status_id}: {e}")
            return "Internal server error"