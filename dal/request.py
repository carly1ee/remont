# dal/request.py

from typing import List, Optional, Dict, Union
from db_manager import DatabaseManager
import logging

logger = logging.getLogger(__name__)

class RequestDAL:
    @staticmethod
    def get_requests_by_engineer(engineer_id: int, page: int = 1, per_page: int = 10) -> Union[List[Dict], str]:
        """
        Получает список заявок инженера с пагинацией
        """
        try:
            offset = (page - 1) * per_page

            with DatabaseManager.get_cursor() as cursor:
                query = """
                    SELECT 
                        request_id,
                        operator_id,
                        engineer_id,
                        status_id,
                        phone,
                        adress AS address,
                        techniq AS equipment,
                        description,
                        creation_date,
                        assigned_time,
                        in_works_time,
                        done_time
                    FROM request
                    WHERE engineer_id = %s
                    ORDER BY creation_date DESC
                    LIMIT %s OFFSET %s;
                """
                cursor.execute(query, (engineer_id, per_page, offset))
                result = cursor.fetchall()

                logger.info(f"Found {len(result)} requests for engineer {engineer_id} (page {page})")
                return result

        except Exception as e:
            logger.error(f"Error fetching requests for engineer {engineer_id}: {e}")
            return "Internal server error"