"""
Главный модуль копирования сделок с Hyperliquid.
"""

import time
from typing import List, Dict, Any

from .config.load_env import load_environment
from .config.get_settings import build_settings
from .utils.get_logger import get_logger
from .database.get_connection import get_connection
from .database.fetch_new_positions import fetch_new_positions
from .database.delete_position import delete_position
from .hyperliquid.get_account_state import get_account_state
from .hyperliquid.get_open_positions import get_open_positions
from .hyperliquid.calculate_position_size import calculate_position_size_usd
from .hyperliquid.place_order import place_market_order
from .positions.check_position_exists import check_position_exists
from .telegram.send_notification import send_telegram_message, format_position_notification


def _process_new_position(
    position: Dict[str, Any],
    open_positions: List[Dict[str, Any]],
    settings,
    account_state: Dict[str, Any],
    logger
) -> bool:
    """
    Обрабатывает одну новую позицию: проверяет существование и открывает, если нужно.

    Args:
        position: Данные позиции из new_positions.
        open_positions: Список уже открытых позиций.
        settings: Настройки приложения.
        account_state: Текущее состояние аккаунта.
        logger: Logger.

    Returns:
        True если позиция была открыта, False если нет.
    """
    coin = position.get("coin", "")
    side = position.get("side", "")
    target_leverage = int(position.get("leverage", "10"))

    logger.info(f"Обработка позиции: {coin} {side} (плечо {target_leverage}x)")

    # Проверяем, есть ли уже такая позиция
    if check_position_exists(open_positions, coin, side):
        logger.info(f"  Позиция {coin} {side} уже открыта. Пропускаем.")
        return False

    # Рассчитываем размер позиции
    size_usd = calculate_position_size_usd(account_state, settings.position_size_percent)
    if size_usd <= 0:
        logger.warning(f"  Недостаточно средств для открытия позиции {coin} {side}.")
        return False

    logger.info(f"  Размер позиции: ${size_usd:.2f} ({settings.position_size_percent}% от баланса)")

    # Пытаемся открыть позицию с указанным плечом
    # Если не получится, попробуем с меньшим плечом (логика fallback)
    leverages_to_try = [target_leverage]
    # Добавляем варианты с уменьшением плеча
    for lev in [20, 10, 5, 3, 1]:
        if lev < target_leverage and lev not in leverages_to_try:
            leverages_to_try.append(lev)

    success = False
    used_leverage = target_leverage

    for leverage in leverages_to_try:
        try:
            logger.info(f"  Открываю позицию {coin} {side} с плечом {leverage}x...")

            order_response = place_market_order(
                api_url=settings.hyperliquid_api_url,
                private_key=settings.hyperliquid_private_key,
                coin=coin,
                side=side,
                size_usd=size_usd,
                leverage=leverage,
                timeout=settings.http_timeout_seconds
            )

            logger.info(f"  ✅ Позиция {coin} {side} открыта успешно с плечом {leverage}x")
            logger.info(f"  Ответ API: {order_response}")
            success = True
            used_leverage = leverage
            break

        except Exception as e:
            logger.error(f"  Ошибка открытия позиции {coin} {side} с плечом {leverage}x: {e}")
            if leverage == leverages_to_try[-1]:
                logger.error(f"  ❌ Не удалось открыть позицию {coin} {side} ни с одним плечом.")
            else:
                logger.info(f"  Пробую с меньшим плечом...")

    # Отправляем уведомление в Telegram
    try:
        message = format_position_notification(coin, side, size_usd, used_leverage, success)
        send_telegram_message(
            bot_token=settings.telegram_bot_token,
            chat_id=settings.telegram_chat_id,
            message=message,
            timeout=settings.http_timeout_seconds
        )
        logger.info(f"  Уведомление отправлено в Telegram")
    except Exception as e:
        logger.error(f"  Ошибка отправки уведомления в Telegram: {e}")

    return success


def _run_single_cycle(settings, logger) -> None:
    """
    Выполняет один цикл проверки новых позиций.

    Args:
        settings: Настройки приложения.
        logger: Logger.
    """
    with get_connection(settings.database_url) as conn:
        # Получаем список новых позиций из БД
        new_positions = fetch_new_positions(conn)

        if not new_positions:
            logger.debug("Новых позиций не найдено.")
            return

        logger.info(f"Найдено новых позиций: {len(new_positions)}")

        # Получаем текущее состояние аккаунта
        try:
            account_state = get_account_state(
                api_url=settings.hyperliquid_api_url,
                wallet_address=settings.wallet_address,
                timeout=settings.http_timeout_seconds
            )
        except Exception as e:
            logger.error(f"Ошибка получения состояния аккаунта: {e}")
            return

        # Получаем список уже открытых позиций
        open_positions = get_open_positions(account_state)
        logger.info(f"Текущих открытых позиций: {len(open_positions)}")

        # Обрабатываем каждую новую позицию
        for position in new_positions:
            position_id = position.get("id")
            try:
                processed = _process_new_position(
                    position=position,
                    open_positions=open_positions,
                    settings=settings,
                    account_state=account_state,
                    logger=logger
                )

                # Удаляем обработанную позицию из new_positions
                if processed or True:  # Удаляем в любом случае после обработки
                    delete_position(conn, position_id)
                    logger.info(f"Позиция ID {position_id} удалена из new_positions.")

            except Exception as e:
                logger.error(f"Ошибка обработки позиции ID {position_id}: {e}")


def run_executor_loop(env_path: str | None = None) -> None:
    """
    Запускает бесконечный цикл мониторинга таблицы new_positions.

    Args:
        env_path: Путь к .env файлу (опционально).
    """
    load_environment(env_path)
    settings = build_settings()
    logger = get_logger("trade_executor.main")

    logger.info("Запуск Trade Executor")
    logger.info(f"Кошелёк: {settings.wallet_address}")
    logger.info(f"Интервал опроса: {settings.poll_interval_seconds} сек")
    logger.info(f"Размер позиции: {settings.position_size_percent}% от баланса")

    iteration = 0

    try:
        while True:
            iteration += 1
            logger.info(f"--- Цикл #{iteration} ---")

            try:
                _run_single_cycle(settings, logger)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.error(f"Ошибка в цикле: {e}")

            logger.info(f"Ожидание {settings.poll_interval_seconds} секунд...")
            time.sleep(settings.poll_interval_seconds)

    except KeyboardInterrupt:
        logger.info("Остановка Trade Executor (Ctrl+C)")

