"""
Модуль получения состояния аккаунта Hyperliquid.
"""

import requests
from typing import Dict, Any


def get_account_state(api_url: str, wallet_address: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Получает состояние аккаунта пользователя через Hyperliquid API.

    Args:
        api_url: URL API Hyperliquid.
        wallet_address: Адрес кошелька пользователя.
        timeout: Таймаут запроса в секундах.

    Returns:
        Словарь с данными состояния аккаунта.
    """
    endpoint = f"{api_url}/info"
    payload = {
        "type": "clearinghouseState",
        "user": wallet_address
    }

    response = requests.post(endpoint, json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()

