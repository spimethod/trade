"""
Модуль получения переменных окружения.
"""

import os


def get_env_var(name: str, required: bool = False, default: str | None = None) -> str | None:
    """
    Получает переменную окружения.

    Args:
        name: Имя переменной.
        required: Является ли переменная обязательной.
        default: Значение по умолчанию.

    Returns:
        Значение переменной или None.

    Raises:
        ValueError: Если переменная обязательна, но не установлена.
    """
    value = os.environ.get(name, default)
    if required and not value:
        raise ValueError(f"Переменная окружения {name} обязательна, но не установлена.")
    return value

