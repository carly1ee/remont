from typing import List, Dict
from db_manager import DatabaseManager
import logging

logger = logging.getLogger(__name__)

class RequestHistoryDAL:
    @staticmethod
    def get_request_history(request_id: int) -> List[Dict]:
        try:
            with DatabaseManager.get_cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        rh.field_name,
                        rh.old_value,
                        rh.new_value,
                        rh.changed_at,
                        u.name AS changer_name
                    FROM request_history rh
                    JOIN users u ON rh.changer_id = u.user_id
                    WHERE rh.request_id = %s
                    ORDER BY rh.changed_at DESC;
                """, (request_id,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching history for request {request_id}: {e}")
            return []