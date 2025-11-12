"""
Модуль проверки наличия позиции в списке открытых.
"""

from typing import List, Dict, Any


def check_position_exists(
    open_positions: List[Dict[str, Any]],
    coin: str,
    side: str
) -> bool:
    """
    Проверяет, есть ли уже открытая позиция по данному активу и направлению.

    Args:
        open_positions: Список открытых позиций с полями coin, side.
        coin: Монета для проверки.
        side: Направление (LONG/SHORT).

    Returns:
        True если позиция существует, иначе False.
    """
    for position in open_positions:
        if position.get("coin") == coin and position.get("side") == side:
            return True
    return False

