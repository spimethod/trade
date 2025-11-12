"""
Модуль получения новых позиций из таблицы new_positions.
"""

from typing import List, Dict, Any
import psycopg


def fetch_new_positions(connection: psycopg.Connection) -> List[Dict[str, Any]]:
    """
    Получает все записи из таблицы new_positions.

    Args:
        connection: Подключение к базе данных.

    Returns:
        Список словарей с данными позиций.
    """
    query = """
        SELECT
            id,
            position_signature,
            coin,
            side,
            size,
            entry_price,
            current_price,
            unrealized_pnl,
            pnl_percent,
            leverage,
            margin_used,
            liquidation_price,
            detected_at
        FROM new_positions
        ORDER BY detected_at DESC;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

    return [dict(zip(columns, row)) for row in rows]

