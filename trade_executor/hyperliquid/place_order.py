"""
Модуль открытия позиции на Hyperliquid с использованием приватного ключа.
"""

from typing import Dict, Any
from eth_account import Account
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange


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

    # Создаём wallet из приватного ключа
    wallet = Account.from_key(private_key)
    
    # Инициализируем Info и Exchange клиенты
    info = Info(api_url, skip_ws=True)
    exchange = Exchange(wallet, api_url)
    
    # Определяем направление: True = Buy (LONG), False = Sell (SHORT)
    is_buy = (side == "LONG")
    
    # Получаем текущую цену и метаданные для расчёта размера в токенах
    mid_price = float(info.all_mids()[coin])
    meta = info.meta()
    
    # Находим количество десятичных знаков для этого токена
    sz_decimals = 8  # По умолчанию
    for asset in meta['universe']:
        if asset['name'] == coin:
            sz_decimals = asset['szDecimals']
            break
    
    # Конвертируем USD в размер позиции в токенах
    sz = round(size_usd / mid_price, sz_decimals)
    
    # Устанавливаем плечо (leverage)
    # Примечание: update_leverage принимает asset index, а не coin
    # Находим asset index
    asset_index = None
    for idx, asset in enumerate(meta['universe']):
        if asset['name'] == coin:
            asset_index = idx
            break
    
    if asset_index is not None:
        try:
            # Устанавливаем leverage через asset index и is_cross
            exchange.update_leverage(leverage, asset_index, is_cross=True)
        except Exception as e:
            # Если не получилось установить leverage, продолжаем без него
            pass
    
    # Открываем рыночный ордер с 5% slippage
    result = exchange.market_open(coin, is_buy, sz, None, 0.05)
    
    return result

