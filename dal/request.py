# dal/request.py

from typing import List, Dict, Union, Optional
from db_manager import DatabaseManager
import logging
from datetime import datetime, timedelta

from dal.status import StatusDAL

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
            customer_name: str,
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
                            phone, adress, techniq, description, customer_name,
                            creation_date, assigned_time
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)
                        RETURNING request_id, creation_date, assigned_time;
                    """

                # Если указан engineer_id — assigned_time = creation_date
                assigned_time = 'NOW()' if engineer_id else 'NULL'

                cursor.execute(query, (
                    operator_id, engineer_id, status_id,
                    phone, address, techniq, description, customer_name,
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
                        customer_name,
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
    def get_completed_requests_with_total(engineer_id: int, page: int = 1, per_page: int = 10) -> Union[Dict, str]:
        """
        Получает список выполненных заявок (status_id = 4) и общее количество
        """
        try:
            offset = (page - 1) * per_page

            with DatabaseManager.get_cursor() as cursor:
                # Подсчёт общего количества
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM request
                    WHERE engineer_id = %s AND status_id = 4;
                """, (engineer_id,))
                total = cursor.fetchone()['count']

                # Получение данных с пагинацией
                query = """
                    SELECT 
                        request_id,
                        operator_id,
                        engineer_id,
                        status_id,
                        customer_name,
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

                return {
                    'requests': result,
                    'total': total
                }

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

                if role_id == 3 or role_id == 2:  # Админ или Оператор — могут всё
                    allowed_fields = list(updates.keys())
                elif role_id == 1:  # Инженер — только временные поля
                    allowed_fields = [f for f in updates.keys()
                                      if f in ['assigned_time', 'in_works_time', 'done_time']]
                else:
                    return "Access denied"

                if not allowed_fields:
                    return "No valid fields to update"

                # Если обновляется статус — делаем запись в историю
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
                    old_value = str(request_data[field]) if request_data[field] is not None else None
                    new_value = str(updates[field])

                    if field == 'status_id':
                        old_status = StatusDAL.get_status_by_id(int(old_value)) if old_value else None
                        new_status = StatusDAL.get_status_by_id(int(new_value)) if new_value else None
                        old_value = old_status['status'] if old_status and isinstance(old_status, dict) else old_value
                        new_value = new_status['status'] if new_status and isinstance(new_status, dict) else new_value

                    cursor.execute("""
                        INSERT INTO request_history (
                            request_id, changer_id, field_name, old_value, new_value
                        )
                        VALUES (%s, %s, %s, %s, %s);
                    """, (
                        request_id,
                        user_id,
                        field,
                        old_value,
                        new_value
                    ))

                logger.info(f"Request {request_id} updated by user {user_id}")
                return dict(updated_request)

        except Exception as e:
            logger.error(f"Error updating request {request_id}: {e}")
            return "Internal server error"

        except Exception as e:
            logger.error(f"Error updating request {request_id}: {e}")
            return "Internal server error"

    @staticmethod
    def count_completed_requests(engineer_id: int, start_date: datetime, end_date: datetime) -> Union[int, str]:
        """
        Считает количество выполненных заявок (status_id=4) у инженера за период
        """
        try:
            with DatabaseManager.get_cursor() as cursor:
                query = """
                        SELECT COUNT(*) AS count
                        FROM request
                        WHERE status_id = 4
                          AND engineer_id = %s
                          AND creation_date >= %s
                          AND creation_date <= %s;
                    """
                cursor.execute(query, (engineer_id, start_date, end_date))
                result = cursor.fetchone()['count']
                return result if result is not None else 0

        except Exception as e:
            logger.error(f"Error fetching completed requests for engineer {engineer_id}: {e}")
            return "Internal server error"


    @staticmethod
    def count_all_engineers_completed_requests(start_date: datetime, end_date: datetime) -> Union[List[Dict], str]:
        """
        Возвращает список: инженер и количество его выполненных заявок за период
        """
        try:
            with DatabaseManager.get_cursor() as cursor:
                query = """
                    SELECT 
                        r.engineer_id,
                        u.name AS engineer_name,
                        COUNT(*) AS count
                    FROM request r
                    JOIN users u ON r.engineer_id = u.user_id
                    WHERE r.status_id = 4
                      AND r.creation_date >= %s
                      AND r.creation_date <= %s
                    GROUP BY r.engineer_id, u.name;
                """
                cursor.execute(query, (start_date, end_date))
                return cursor.fetchall()

        except Exception as e:
            logger.error(f"Error fetching all engineers' completed requests: {e}")
            return "Internal server error"

    @staticmethod
    def get_request_stats_this_month() -> Union[Dict, str]:
        """
        Получает статистику по заявкам за текущий месяц
        """
        try:
            with DatabaseManager.get_cursor() as cursor:
                # Определяем начало текущего месяца
                today = datetime.today()
                start_date = datetime(today.year, today.month, 1)
                end_date = today  # до сегодняшней даты

                query = """
                    SELECT 
                        COUNT(*) FILTER (WHERE status_id = 1) AS total_created,
                        COUNT(*) FILTER (WHERE status_id = 2) AS total_assigned,
                        COUNT(*) FILTER (WHERE status_id = 3) AS total_in_works,
                        COUNT(*) FILTER (WHERE status_id = 4) AS total_done
                    FROM request
                    WHERE creation_date >= %s AND creation_date <= %s;
                """
                cursor.execute(query, (start_date, end_date))
                result = cursor.fetchone()

                return {
                    'total_created': result['total_created'] or 0,
                    'total_assigned': result['total_assigned'] or 0,
                    'total_in_works': result['total_in_works'] or 0,
                    'total_done': result['total_done'] or 0,
                    'period': {
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat()
                    }
                }

        except Exception as e:
            logger.error(f"Error fetching monthly request stats: {e}")
            return "Internal server error"

    @staticmethod
    def get_filtered_requests(
            engineer_id: Optional[int] = None,
            status_ids: Optional[list] = None,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            page: int = 1,
            per_page: int = 10
    ) -> Union[List[Dict], str]:
        """
        Получает список заявок с фильтрами по инженеру, статусу и периоду с пагинацией
        """
        try:
            offset = (page - 1) * per_page

            with DatabaseManager.get_cursor() as cursor:
                query = """
                    SELECT 
                        r.request_id,
                        r.operator_id,
                        r.engineer_id,
                        r.status_id,
                        u.name AS engineer_name,
                        s.status AS status_name,
                        r.phone,
                        r.adress AS address,
                        r.techniq AS equipment,
                        r.description,
                        r.creation_date,
                        r.assigned_time,
                        r.in_works_time,
                        r.done_time
                    FROM request r
                    LEFT JOIN users u ON r.engineer_id = u.user_id
                    LEFT JOIN status s ON r.status_id = s.status_id
                    WHERE 1=1
                """

                params = []

                if engineer_id is not None:
                    query += " AND r.engineer_id = %s"
                    params.append(engineer_id)

                if status_ids:
                    query += " AND r.status_id = ANY(%s)"
                    params.append(status_ids)

                if start_date:
                    query += " AND r.creation_date >= %s"
                    params.append(start_date)

                if end_date:
                    query += " AND r.creation_date <= %s"
                    params.append(end_date)

                query += " ORDER BY r.creation_date DESC LIMIT %s OFFSET %s"

                # Добавляем параметры пагинации
                params.extend([per_page, offset])

                cursor.execute(query, params)
                return cursor.fetchall()

        except Exception as e:
            logger.error(f"Error fetching filtered requests: {e}")
            return "Internal server error"

    @staticmethod
    def get_engineers_stats_with_balance_and_requests() -> Union[List[Dict], str]:
        """
        Получает статистику по всем инженерам за текущий месяц:
        - баланс
        - количество активных заявок (статусы 2 и 4)
        - количество завершённых заявок за месяц (статус 4)
        """
        try:
            with DatabaseManager.get_cursor() as cursor:
                # Определяем начало месяца
                today = datetime.today()
                start_of_month = datetime(today.year, today.month, 1)

                query = """
                    SELECT 
                        u.user_id,
                        u.name AS engineer_name,

                        COALESCE(ep.balance, 0) AS balance,

                        COUNT(r_all.request_id) FILTER (WHERE r_all.status_id IN (2, 4)) AS active_requests,

                        COUNT(r_done.request_id) FILTER (WHERE r_done.status_id = 4 AND r_done.done_time >= %s) AS completed_in_month
                    FROM users u
                    JOIN roles r ON u.role_id = r.role_id AND r.role = 'engineer'
                    LEFT JOIN engineer_profile ep ON u.user_id = ep.user_id
                    LEFT JOIN request r_all ON r_all.engineer_id = u.user_id
                    LEFT JOIN request r_done ON r_done.engineer_id = u.user_id
                    GROUP BY u.user_id, ep.balance
                    ORDER BY u.user_id;
                """
                cursor.execute(query, (start_of_month,))
                return cursor.fetchall()

        except Exception as e:
            logger.error(f"Error fetching engineers stats: {e}")
            return "Internal server error"

    @staticmethod
    def get_assigned_and_in_works_requests(engineer_id: int) -> Union[List[Dict], str]:
        """
        Получает заявки инженера со статусами 2 и 3,
        где assigned_time <= текущее время
        """
        try:
            with DatabaseManager.get_cursor() as cursor:
                query = """
                    SELECT 
                        request_id,
                        operator_id,
                        engineer_id,
                        status_id,
                        customer_name,
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
                      AND status_id IN (2, 3)
                      AND assigned_time <= NOW()
                    ORDER BY assigned_time DESC;
                """
                cursor.execute(query, (engineer_id,))
                return cursor.fetchall()

        except Exception as e:
            logger.error(f"Error fetching requests for engineer {engineer_id}: {e}")
            return "Internal server error"