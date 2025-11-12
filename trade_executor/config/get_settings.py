"""
Модуль построения настроек приложения из переменных окружения.
"""

from dataclasses import dataclass
from .get_env_var import get_env_var


@dataclass
class Settings:
    """Настройки приложения."""

    # База данных
    database_url: str

    # Hyperliquid
    hyperliquid_api_url: str
    hyperliquid_private_key: str  # Хранится ТОЛЬКО в Railway Variables
    wallet_address: str
    position_size_percent: float  # % от общего баланса для каждой сделки

    # Telegram
    telegram_bot_token: str
    telegram_chat_id: str

    # Мониторинг
    poll_interval_seconds: int
    http_timeout_seconds: int


def build_settings() -> Settings:
    """
    Собирает настройки из переменных окружения.

    Returns:
        Объект Settings с конфигурацией.
    """
    # База данных (Railway автоматически прокидывает DATABASE_URL)
    database_url = get_env_var("DATABASE_URL", required=True)

    # Hyperliquid настройки
    api_url = get_env_var(
        "HYPERLIQUID_API_URL",
        default="https://api.hyperliquid.xyz"
    )
    private_key = get_env_var("HYPERLIQUID_PRIVATE_KEY", required=True)
    wallet_address = get_env_var("WALLET_ADDRESS", required=True)

    position_size_str = get_env_var("POSITION_SIZE_PERCENT", default="5.0")
    position_size_percent = float(position_size_str)

    # Telegram
    telegram_bot_token = get_env_var("TELEGRAM_BOT_TOKEN", required=True)
    telegram_chat_id = get_env_var("TELEGRAM_CHAT_ID", required=True)

    # Мониторинг
    poll_interval_str = get_env_var("POLL_INTERVAL_SECONDS", default="5")
    poll_interval_seconds = int(poll_interval_str)

    http_timeout_str = get_env_var("HTTP_TIMEOUT_SECONDS", default="10")
    http_timeout_seconds = int(http_timeout_str)

    return Settings(
        database_url=database_url,
        hyperliquid_api_url=api_url,
        hyperliquid_private_key=private_key,
        wallet_address=wallet_address,
        position_size_percent=position_size_percent,
        telegram_bot_token=telegram_bot_token,
        telegram_chat_id=telegram_chat_id,
        poll_interval_seconds=poll_interval_seconds,
        http_timeout_seconds=http_timeout_seconds,
    )

