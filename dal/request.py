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

    @staticmethod
    def get_completed_requests(engineer_id: int, page: int = 1, per_page: int = 10) -> Union[List[Dict], str]:
        """
        Получает список выполненных заявок (status_id = 4) для конкретного инженера
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
                        WHERE engineer_id = %s AND status_id = 4
                        ORDER BY done_time DESC
                        LIMIT %s OFFSET %s;
                    """
                cursor.execute(query, (engineer_id, per_page, offset))
                result = cursor.fetchall()

                logger.info(f"Found {len(result)} completed requests for engineer {engineer_id} (page {page})")
                return result

        except Exception as e:
            logger.error(f"Error fetching completed requests for engineer {engineer_id}: {e}")
            return "Internal server error"

    @staticmethod
    def update_request(
            user_id: int,
            role_id: int,
            request_id: int,
            updates: Dict[str, any]
    ) -> Union[Dict[str, any], str]:
        """
        Обновляет заявку с проверкой прав пользователя.
        Логирует изменения в request_history.
        """

        try:
            with DatabaseManager.get_cursor() as cursor:
                # Получаем текущие данные заявки
                cursor.execute("""
                    SELECT * FROM request WHERE request_id = %s;
                """, (request_id,))
                request_data = cursor.fetchone()

                if not request_data:
                    return "Request not found"

                allowed_fields = []

                if role_id == 3:  # Админ — может всё
                    allowed_fields = list(updates.keys())
                elif role_id == 2:  # Оператор — тоже может всё
                    allowed_fields = list(updates.keys())
                elif role_id == 1:  # Инженер — только временные поля
                    allowed_fields = [f for f in updates.keys()
                                      if f in ['assigned_time', 'in_works_time', 'done_time']]
                else:
                    return "Access denied"

                if not allowed_fields:
                    return "No valid fields to update"
                # Формируем SQL-обновление
                set_clause = ', '.join([f"{field} = %s" for field in allowed_fields])
                query = f"""
                    UPDATE request
                    SET {set_clause}
                    WHERE request_id = %s
                    RETURNING *;
                """
                params = [updates[field] for field in allowed_fields]
                params.append(request_id)

                cursor.execute(query, tuple(params))
                updated_request = cursor.fetchone()
                # Логируем каждое изменение
                for field in allowed_fields:
                    cursor.execute("""
                        INSERT INTO request_history (
                            request_id, changer_id, field_name, old_value, new_value
                        )
                        VALUES (%s, %s, %s, %s, %s);
                    """, (
                        request_id,
                        user_id,
                        field,
                        str(request_data[field]) if request_data[field] is not None else None,
                        str(updates[field])
                    ))
                logger.info(f"Request {request_id} updated by user {user_id}")
                return dict(updated_request)

        except Exception as e:
            logger.error(f"Error updating request {request_id}: {e}")
            return "Internal server error"