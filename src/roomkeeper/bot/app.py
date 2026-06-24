from __future__ import annotations

from telegram.ext import Application, ApplicationBuilder, CommandHandler

from roomkeeper.bot.config import BotConfig, load_bot_config
from roomkeeper.bot.handlers import help_command, start_command


def build_application(config: BotConfig) -> Application:
    """Создает Telegram-приложение и регистрирует команды."""

    application = ApplicationBuilder().token(config.token).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    return application


def run_bot() -> None:
    """Запускает Telegram-бота."""

    config = load_bot_config()
    application = build_application(config)

    print("RoomKeeper bot is running. Press Ctrl+C to stop.")
    application.run_polling()
