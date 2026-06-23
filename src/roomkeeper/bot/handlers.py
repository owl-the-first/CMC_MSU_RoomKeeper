from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /start."""

    user = update.effective_user
    name = user.first_name if user and user.first_name else "студент"

    text = (
        f"Привет, {name}!\n\n"
        "Я RoomKeeper — бот для поиска и бронирования свободных аудиторий ВМК МГУ.\n\n"
        "Пока я умею только запускаться и показывать справку.\n"
        "На следующих этапах появится поиск свободных аудиторий и создание заявок.\n\n"
        "Напиши /help, чтобы посмотреть список команд."
    )

    if update.message is not None:
        await update.message.reply_text(text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /help."""

    text = (
        "Доступные команды:\n\n"
        "/start — запустить бота\n"
        "/help — показать справку\n\n"
        "Скоро появятся:\n"
        "/free — найти свободные аудитории\n"
        "/book — создать заявку на бронирование\n"
        "/my_bookings — посмотреть свои заявки"
    )

    if update.message is not None:
        await update.message.reply_text(text)
