from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from roomkeeper.booking.bookings import create_booking_request
from roomkeeper.bot.book_command import (
    get_book_command_usage,
    parse_book_room_request,
)
from roomkeeper.bot.free_command import (
    format_free_rooms_message,
    get_free_command_usage,
    parse_free_rooms_request,
)
from roomkeeper.search.free_rooms import find_free_rooms


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /start."""

    user = update.effective_user
    name = user.first_name if user and user.first_name else "студент"

    text = (
        f"Привет, {name}!\n\n"
        "Я RoomKeeper — бот для поиска и бронирования свободных аудиторий ВМК МГУ.\n\n"
        "Доступные команды:\n"
        "/help — показать справку\n"
        "/free — найти свободные аудитории\n"
        "/book — создать заявку на бронирование"
    )

    if update.message is not None:
        await update.message.reply_text(text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /help."""

    text = (
        "Доступные команды:\n\n"
        "/start — запустить бота\n"
        "/help — показать справку\n"
        "/free — найти свободные аудитории\n"
        "/book — создать заявку на бронирование\n\n"
        f"{get_free_command_usage()}\n\n"
        f"{get_book_command_usage()}\n\n"
        "Скоро появится:\n"
        "/my_bookings — посмотреть свои заявки"
    )

    if update.message is not None:
        await update.message.reply_text(text)


async def free_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /free."""

    if update.message is None:
        return

    try:
        request = parse_free_rooms_request(context.args)
    except ValueError as error:
        await update.message.reply_text(str(error))
        return

    session_factory = context.application.bot_data.get("session_factory")

    if session_factory is None:
        await update.message.reply_text(
            "Ошибка настройки бота: не удалось подключиться к базе данных."
        )
        return

    with session_factory() as session:
        rooms = find_free_rooms(
            session=session,
            booking_date=request.booking_date,
            start_time=request.start_time,
            end_time=request.end_time,
            week_type=request.week_type,
            room_query=request.room_query,
        )

    await update.message.reply_text(format_free_rooms_message(request, rooms))


async def book_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /book."""

    if update.message is None:
        return

    try:
        request = parse_book_room_request(context.args)
    except ValueError as error:
        await update.message.reply_text(str(error))
        return

    session_factory = context.application.bot_data.get("session_factory")

    if session_factory is None:
        await update.message.reply_text(
            "Ошибка настройки бота: не удалось подключиться к базе данных."
        )
        return

    user = update.effective_user

    if user is None:
        await update.message.reply_text("Не удалось определить пользователя Telegram.")
        return

    user_name = user.username or user.full_name

    with session_factory() as session:
        result = create_booking_request(
            session=session,
            room_name=request.room_name,
            user_telegram_id=str(user.id),
            user_name=user_name,
            booking_date=request.booking_date,
            start_time=request.start_time,
            end_time=request.end_time,
            purpose=request.purpose,
            week_type=request.week_type,
        )

    await update.message.reply_text(result.message)
