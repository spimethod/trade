"""
Модуль получения подключения к PostgreSQL.
"""

from contextlib import contextmanager
from typing import Generator

import psycopg


@contextmanager
def get_connection(dsn: str) -> Generator[psycopg.Connection, None, None]:
    """
    Контекстный менеджер подключения к PostgreSQL.

    Args:
        dsn: Строка подключения.
    """
    connection = psycopg.connect(dsn)
    try:
        yield connection
    finally:
        connection.close()

