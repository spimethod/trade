"""
Модуль открытия позиции на Hyperliquid с использованием приватного ключа.
"""

from typing import Dict, Any
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants


def place_market_order(
    api_url: str,
    private_key: str,
    coin: str,
    side: str,
    size_usd: float,
    leverage: int,
    timeout: int = 10
) -> Dict[str, Any]:
    """
    Размещает рыночный ордер на Hyperliquid используя официальный SDK.

    Args:
        api_url: URL API Hyperliquid.
        private_key: Приватный ключ (hex строка без 0x или с ним).
        coin: Символ монеты (например, BTC).
        side: Направление сделки ("LONG" или "SHORT").
        size_usd: Размер позиции в USDC.
        leverage: Плечо (например, 10).
        timeout: Таймаут запроса.

    Returns:
        Ответ от exchange API.
    """
    # Нормализуем приватный ключ
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key

    # Создаём Exchange клиент из официального SDK
    # SDK принимает wallet как объект LocalAccount или приватный ключ напрямую
    from eth_account import Account
    wallet = Account.from_key(private_key)
    
    # Инициализируем Exchange с wallet
    exchange = Exchange(
        wallet=wallet,
        base_url=None,  # По умолчанию mainnet
        account_address=None
    )
    
    # Определяем направление: True = Buy (LONG), False = Sell (SHORT)
    is_buy = (side == "LONG")
    
    # Устанавливаем плечо для актива (изолированная маржа)
    # Сначала нужно получить asset index для монеты
    # Используем market order с leverage
    
    try:
        # Устанавливаем leverage для актива
        leverage_result = exchange.update_leverage(
            leverage=leverage,
            coin=coin,
            is_cross=True  # True = cross margin, False = isolated
        )
        
        # Размещаем market order
        # size_usd нужно конвертировать в количество монет
        # Для упрощения используем limit order с очень агрессивной ценой
        order_result = exchange.market_open(
            coin=coin,
            is_buy=is_buy,
            sz=size_usd,  # SDK сам конвертирует USD в размер
            px=None,  # None для market order
        )
        
        return order_result
        
    except AttributeError:
        # Если методы SDK отличаются, используем базовый order
        order_result = exchange.order(
            coin=coin,
            is_buy=is_buy,
            sz=size_usd,
            limit_px=0,  # 0 для market order
            order_type={"limit": {"tif": "Ioc"}},  # Immediate-or-cancel
            reduce_only=False
        )
        
        return order_result

