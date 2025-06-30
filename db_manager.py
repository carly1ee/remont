from typing import Iterator
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from contextlib import contextmanager
import logging
from config import Settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    _pool = None

    @classmethod
    def initialize(cls, config: Settings):
        """Инициализация пула соединений при старте приложения"""
        if cls._pool is None:
            try:
                cls._pool = pool.ThreadedConnectionPool(
                    minconn=1,
                    maxconn=10,
                    user=config.USER,
                    password=config.PASSWORD,
                    host=config.HOST_NAME,
                    port=config.PORT_NAME,
                    database=config.DB_NAME
                )
                logger.info("Database connection pool initialized")
            except Exception as e:
                logger.error(f"Connection pool initialization failed: {e}")
                raise

    @classmethod
    @contextmanager
    def get_cursor(cls) -> Iterator[RealDictCursor]:
        """Контекстный менеджер для безопасной работы с курсором"""
        conn = None
        try:
            conn = cls._pool.getconn()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                yield cursor
            conn.commit()
        except psycopg2.Error as e:
            logger.error(f"Database error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                cls._pool.putconn(conn)

    @classmethod
    def close_all(cls):
        """Закрыть все соединения при завершении приложения"""
        if cls._pool:
            cls._pool.closeall()
            logger.info("All database connections closed")