"""
Модуль расчёта размера позиции на основе процента от баланса.
"""

from typing import Dict, Any


def calculate_position_size_usd(
    account_state: Dict[str, Any],
    size_percent: float
) -> float:
    """
    Рассчитывает размер позиции в USD на основе процента от общего баланса.

    Args:
        account_state: Состояние аккаунта от API.
        size_percent: Процент от общего баланса (например, 5.0 для 5%).

    Returns:
        Размер позиции в USDC.
    """
    margin_summary = account_state.get("marginSummary", {})
    
    # Пробуем получить accountValue из разных мест
    account_value_str = margin_summary.get("accountValue", "0")
    
    # Hyperliquid иногда возвращает строки вместо чисел
    try:
        account_value = float(account_value_str)
    except (ValueError, TypeError):
        account_value = 0.0
    
    # Если accountValue = 0, пробуем взять из withdrawable или другого поля
    if account_value <= 0:
        withdrawable = account_state.get("withdrawable", "0")
        try:
            account_value = float(withdrawable)
        except (ValueError, TypeError):
            pass

    if account_value <= 0:
        return 0.0

    position_size = (account_value * size_percent) / 100.0
    return position_size

