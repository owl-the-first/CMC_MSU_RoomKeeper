from __future__ import annotations

from telegram.ext import Application, ApplicationBuilder, CommandHandler

from roomkeeper.bot.config import BotConfig, load_bot_config
from roomkeeper.bot.handlers import (
    book_command,
    cancel_booking_command,
    free_command,
    help_command,
    my_bookings_command,
    start_command,
)
from roomkeeper.db.session import get_session_factory


def build_application(config: BotConfig) -> Application:
    """Создаёт Telegram-приложение и регистрирует команды."""
    application = (
        ApplicationBuilder()
        .token(config.token)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .pool_timeout(30)
        .get_updates_connect_timeout(30)
        .get_updates_read_timeout(30)
        .build()
    )

    application.bot_data["session_factory"] = get_session_factory(config.database_url)

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("free", free_command))
    application.add_handler(CommandHandler("book", book_command))
    application.add_handler(CommandHandler("my_bookings", my_bookings_command))
    application.add_handler(CommandHandler("cancel_booking", cancel_booking_command))
    application.add_handler(CommandHandler("cancel", cancel_booking_command))

    return application


def run_bot() -> None:
    """Запускает Telegram-бота."""
    config = load_bot_config()
    application = build_application(config)

    print("RoomKeeper bot is running. Press Ctrl+C to stop.")
    application.run_polling()
