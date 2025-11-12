"""
Модуль загрузки переменных окружения.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_environment(env_path: str | None = None) -> None:
    """
    Загружает переменные из .env файла.

    Args:
        env_path: Путь к .env файлу (по умолчанию .env в корне проекта).
    """
    if env_path:
        load_dotenv(env_path)
    else:
        # Ищем .env в корне проекта
        project_root = Path(__file__).parent.parent.parent
        env_file = project_root / ".env"
        if env_file.exists():
            load_dotenv(env_file)
        else:
            # Railway автоматически прокидывает переменные
            pass

