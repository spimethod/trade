"""
Модуль извлечения открытых позиций из состояния аккаунта.
"""

from typing import Dict, Any, List


def get_open_positions(account_state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Извлекает открытые позиции из ответа clearinghouseState.

    Args:
        account_state: Состояние аккаунта от API.

    Returns:
        Список открытых позиций с полями coin, side, size.
    """
    asset_positions = account_state.get("assetPositions", [])
    positions = []

    for entry in asset_positions:
        pos = entry.get("position", {})
        coin = pos.get("coin", "")
        raw_size = float(pos.get("szi", 0) or 0)

        if raw_size == 0:
            continue

        if raw_size > 0:
            side = "LONG"
            size = raw_size
        else:
            side = "SHORT"
            size = abs(raw_size)

        positions.append({
            "coin": coin,
            "side": side,
            "size": size
        })

    return positions

