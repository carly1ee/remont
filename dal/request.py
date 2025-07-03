# dal/request.py

from typing import List, Dict, Union, Optional
from db_manager import DatabaseManager
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RequestDAL:
    @staticmethod
    def create_request(
            operator_id: int,
            status_id: int,
            phone: str,
            address: str,
            techniq: str,
            description: str,
            engineer_id: Optional[int] = None
    ) -> Union[dict, str]:
        """
        Создаёт заявку и проставляет время создания и назначенного инженера (если есть)
        Возвращает словарь с данными заявки или сообщение об ошибке
        """
        try:
            with DatabaseManager.get_cursor() as cursor:
                # Формируем запрос
                query = """
                        INSERT INTO request (
                            operator_id, engineer_id, status_id, 
                            phone, adress, techniq, description,
                            creation_date, assigned_time
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s)
                        RETURNING request_id, creation_date, assigned_time;
                    """

                # Если указан engineer_id — assigned_time = creation_date
                assigned_time = 'NOW()' if engineer_id else 'NULL'

                cursor.execute(query, (
                    operator_id, engineer_id, status_id,
                    phone, address, techniq, description,
                    assigned_time if engineer_id else None
                ))

                result = cursor.fetchone()
                logger.info(f"Request created with ID {result['request_id']}")
                return {
                    "request_id": result["request_id"],
                    "creation_date": result["creation_date"],
                    "assigned_time": result["assigned_time"]
                }

        except Exception as e:
            logger.error(f"Error creating request: {e}")
            return "Internal server error"

    @staticmethod
    def get_requests_by_engineer(
        engineer_id: int,
        status_ids: List[int],
        date_filter: str  # формат 'YYYY-MM-DD'
    ) -> Union[List[Dict], str]:
        """
        Получает заявки инженера по статусам и дате создания (creation_date)
        """

        try:
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
                      AND status_id = ANY(%s)
                      AND DATE(creation_date) = DATE(%s)
                    ORDER BY creation_date DESC;
                """
                cursor.execute(query, (
                    engineer_id,
                    status_ids,
                    date_filter
                ))
                result = cursor.fetchall()

                logger.info(f"Found {len(result)} requests for engineer {engineer_id} on {date_filter}")
                return result

        except Exception as e:
            logger.error(f"Error fetching requests for engineer {engineer_id}: {e}")
            return "Internal server error"