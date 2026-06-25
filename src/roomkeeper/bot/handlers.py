from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from roomkeeper.booking.bookings import (
    cancel_user_booking,
    create_booking_request,
    get_room_names_for_bookings,
    get_user_bookings,
)
from roomkeeper.bot.admin_handlers import notify_admins_about_booking
from roomkeeper.bot.book_command import (
    get_book_command_usage,
    parse_book_room_request,
)
from roomkeeper.bot.free_command import (
    format_free_rooms_message,
    get_free_command_usage,
    parse_free_rooms_request,
)
from roomkeeper.bot.helpers import activate_user_locale, get_session_factory
from roomkeeper.bot.lang_command import (
    format_current_language_message,
    format_lang_changed_message,
    get_lang_command_usage,
    parse_lang_request,
)
from roomkeeper.bot.locale import set_user_locale
from roomkeeper.bot.user_bookings_command import (
    format_user_bookings_message,
    get_cancel_booking_usage,
    get_user_bookings_usage,
    parse_cancel_booking_request,
)
from roomkeeper.i18n import _, set_locale
from roomkeeper.search.free_rooms import find_free_rooms


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /start."""
    user = update.effective_user
    activate_user_locale(
        context,
        str(user.id) if user else None,
        user.language_code if user else None,
    )

    name = user.first_name if user and user.first_name else _("студент")

    text = (
        _("Привет, {name}!").format(name=name)
        + "\n\n"
        + _("Я RoomKeeper — бот для поиска и бронирования свободных аудиторий ВМК МГУ.")
        + "\n\n"
        + _("Доступные команды:\n")
        + "/help — "
        + _("показать справку")
        + "\n"
        + "/free — "
        + _("найти свободные аудитории")
        + "\n"
        + "/book — "
        + _("создать заявку на бронирование")
        + "\n"
        + "/my_bookings — "
        + _("показать мои заявки")
        + "\n"
        + "/cancel_booking — "
        + _("отменить заявку")
        + "\n"
        + "/lang — "
        + _("сменить язык")
    )

    if update.message is not None:
        await update.message.reply_text(text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /help."""
    user = update.effective_user
    activate_user_locale(
        context,
        str(user.id) if user else None,
        user.language_code if user else None,
    )

    text = (
        _("Доступные команды:\n\n")
        + "/start — "
        + _("запустить бота")
        + "\n"
        + "/help — "
        + _("показать справку")
        + "\n"
        + "/free — "
        + _("найти свободные аудитории")
        + "\n"
        + "/book — "
        + _("создать заявку на бронирование")
        + "\n"
        + "/my_bookings — "
        + _("показать мои заявки")
        + "\n"
        + "/cancel_booking — "
        + _("отменить заявку")
        + "\n"
        + "/lang — "
        + _("сменить язык")
        + "\n\n"
        + f"{get_free_command_usage()}\n\n"
        + f"{get_book_command_usage()}\n\n"
        + f"{get_user_bookings_usage()}\n\n"
        + f"{get_cancel_booking_usage()}\n\n"
        + f"{get_lang_command_usage()}"
    )

    if update.message is not None:
        await update.message.reply_text(text)


async def free_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /free."""
    if update.message is None:
        return

    user = update.effective_user
    activate_user_locale(
        context,
        str(user.id) if user else None,
        user.language_code if user else None,
    )

    try:
        request = parse_free_rooms_request(context.args)
    except ValueError as error:
        await update.message.reply_text(str(error))
        return

    session_factory = get_session_factory(context)

    if session_factory is None:
        await update.message.reply_text(
            _("Ошибка настройки бота: не удалось подключиться к базе данных.")
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

    user = update.effective_user
    activate_user_locale(
        context,
        str(user.id) if user else None,
        user.language_code if user else None,
    )

    try:
        request = parse_book_room_request(context.args)
    except ValueError as error:
        await update.message.reply_text(str(error))
        return

    session_factory = get_session_factory(context)

    if session_factory is None:
        await update.message.reply_text(
            _("Ошибка настройки бота: не удалось подключиться к базе данных.")
        )
        return

    if user is None:
        await update.message.reply_text(_("Не удалось определить пользователя Telegram."))
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

    if result.success and result.booking_id is not None:
        await notify_admins_about_booking(context, result.booking_id)


async def my_bookings_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Обрабатывает команду /my_bookings."""
    if update.message is None:
        return

    user = update.effective_user
    activate_user_locale(
        context,
        str(user.id) if user else None,
        user.language_code if user else None,
    )

    session_factory = get_session_factory(context)

    if session_factory is None:
        await update.message.reply_text(
            _("Ошибка настройки бота: не удалось подключиться к базе данных.")
        )
        return

    if user is None:
        await update.message.reply_text(_("Не удалось определить пользователя Telegram."))
        return

    with session_factory() as session:
        bookings = get_user_bookings(
            session=session,
            user_telegram_id=str(user.id),
        )
        room_names = get_room_names_for_bookings(session, bookings)

    await update.message.reply_text(
        format_user_bookings_message(bookings, room_names)
    )


async def cancel_booking_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Обрабатывает команду /cancel_booking."""
    if update.message is None:
        return

    user = update.effective_user
    activate_user_locale(
        context,
        str(user.id) if user else None,
        user.language_code if user else None,
    )

    try:
        booking_id = parse_cancel_booking_request(context.args)
    except ValueError as error:
        await update.message.reply_text(str(error))
        return

    session_factory = get_session_factory(context)

    if session_factory is None:
        await update.message.reply_text(
            _("Ошибка настройки бота: не удалось подключиться к базе данных.")
        )
        return

    if user is None:
        await update.message.reply_text(_("Не удалось определить пользователя Telegram."))
        return

    with session_factory() as session:
        result = cancel_user_booking(
            session=session,
            booking_id=booking_id,
            user_telegram_id=str(user.id),
        )

    await update.message.reply_text(result.message)


async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /lang."""
    if update.message is None:
        return

    user = update.effective_user

    if user is None:
        await update.message.reply_text(_("Не удалось определить пользователя Telegram."))
        return

    if not context.args:
        activate_user_locale(context, str(user.id), user.language_code)
        await update.message.reply_text(format_current_language_message())
        return

    try:
        locale = parse_lang_request(context.args)
    except ValueError as error:
        activate_user_locale(context, str(user.id), user.language_code)
        await update.message.reply_text(str(error))
        return

    set_user_locale(context, str(user.id), locale)
    set_locale(locale)
    await update.message.reply_text(format_lang_changed_message(locale))
