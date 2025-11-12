"""
Модуль удаления обработанной позиции из таблицы new_positions.
"""

import psycopg


def delete_position(connection: psycopg.Connection, position_id: int) -> None:
    """
    Удаляет позицию из таблицы new_positions после обработки.

    Args:
        connection: Подключение к базе данных.
        position_id: ID позиции для удаления.
    """
    query = "DELETE FROM new_positions WHERE id = %s;"

    with connection.cursor() as cursor:
        cursor.execute(query, (position_id,))
    connection.commit()

