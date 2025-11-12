"""
Модуль отправки уведомлений в Telegram.
"""

import requests
from typing import Dict, Any


def send_telegram_message(bot_token: str, chat_id: str, message: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Отправляет сообщение в Telegram через Bot API.

    Args:
        bot_token: Токен Telegram бота.
        chat_id: ID чата для отправки.
        message: Текст сообщения.
        timeout: Таймаут запроса.

    Returns:
        Ответ от Telegram API.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    response = requests.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()


def format_position_notification(coin: str, side: str, size_usd: float, leverage: int, success: bool) -> str:
    """
    Форматирует сообщение об открытии позиции.

    Args:
        coin: Монета.
        side: Направление (LONG/SHORT).
        size_usd: Размер в USD.
        leverage: Плечо.
        success: Успешно ли открыта позиция.

    Returns:
        Форматированное сообщение для Telegram.
    """
    status_emoji = "✅" if success else "❌"
    status_text = "ОТКРЫТА" if success else "ОШИБКА"

    message = f"""
{status_emoji} <b>Позиция {status_text}</b>

<b>Монета:</b> {coin}
<b>Направление:</b> {side}
<b>Размер:</b> ${size_usd:.2f}
<b>Плечо:</b> {leverage}x
    """.strip()

    return message

