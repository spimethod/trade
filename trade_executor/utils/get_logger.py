"""
Модуль настройки логирования.
"""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Создаёт и настраивает logger с выводом в stdout.

    Args:
        name: Имя логгера.

    Returns:
        Настроенный logger.
    """
    logger = logging.getLogger(name)
    
    # Отключаем propagate, чтобы избежать дублирования с root logger
    logger.propagate = False

    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        # Убираем levelname из формата — Railway красит INFO в красный
        formatter = logging.Formatter(
            "%(asctime)s,%(msecs)03d | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

