"""
Модуль открытия позиции на Hyperliquid с использованием приватного ключа.
"""

import json
import time
from typing import Dict, Any
from eth_account import Account
from eth_account.signers.local import LocalAccount


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
    Размещает рыночный ордер на Hyperliquid.

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
    import requests

    # Нормализуем приватный ключ
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key

    # Создаём аккаунт из приватного ключа
    account: LocalAccount = Account.from_key(private_key)
    wallet_address = account.address

    # Определяем is_buy
    is_buy = (side == "LONG")

    # Подготовка запроса (упрощённая структура для рыночного ордера)
    # Используем официальную структуру Hyperliquid SDK
    action = {
        "type": "order",
        "orders": [{
            "a": 0,  # asset index (нужно получать из meta, здесь упрощаем)
            "b": is_buy,
            "p": "0",  # price = 0 для рыночного ордера
            "s": str(size_usd),
            "r": False,  # reduceOnly
            "t": {
                "limit": {
                    "tif": "Ioc"  # Immediate-or-cancel для рыночного ордера
                }
            }
        }],
        "grouping": "na"
    }

    # Временная метка
    timestamp = int(time.time() * 1000)

    # Формируем структуру для подписи
    sign_data = {
        "action": action,
        "nonce": timestamp,
        "vaultAddress": None
    }

    # Подписываем (используем EIP-712)
    # Примечание: полная реализация требует структуру domain и types
    # Здесь используем упрощённый вариант через eth_account
    message_json = json.dumps(sign_data, separators=(',', ':'))
    signature = account.sign_message(text=message_json)

    # Формируем payload для /exchange
    payload = {
        "action": action,
        "nonce": timestamp,
        "signature": {
            "r": hex(signature.r),
            "s": hex(signature.s),
            "v": signature.v
        },
        "vaultAddress": None
    }

    endpoint = f"{api_url}/exchange"
    response = requests.post(endpoint, json=payload, timeout=timeout)
    response.raise_for_status()

    return response.json()

