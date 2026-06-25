from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from roomkeeper.booking.admin import (
    approve_booking,
    get_booking_by_id,
    get_pending_bookings,
    get_room_name_for_booking,
    reject_booking,
)
from roomkeeper.booking.bookings import get_room_names_for_bookings
from roomkeeper.bot.admin_access import is_admin
from roomkeeper.bot.admin_command import (
    build_booking_review_keyboard,
    format_admin_booking_message,
    format_pending_bookings_message,
    format_user_approved_message,
    format_user_rejected_message,
    get_admin_command_usage,
    parse_booking_id_request,
    parse_review_callback_data,
)
from roomkeeper.bot.helpers import activate_user_locale, get_session_factory
from roomkeeper.i18n import _


async def _reply_access_denied(update: Update) -> None:
    """Отправляет сообщение о недостатке прав."""
    if update.message is not None:
        await update.message.reply_text(_("Эта команда доступна только администраторам."))


async def _ensure_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Проверяет права администратора для текстовой команды."""
    user = update.effective_user

    if user is None:
        if update.message is not None:
            await update.message.reply_text(_("Не удалось определить пользователя Telegram."))
        return False

    activate_user_locale(context, str(user.id), user.language_code)

    if not is_admin(context, str(user.id)):
        await _reply_access_denied(update)
        return False

    return True


async def notify_admins_about_booking(
    context: ContextTypes.DEFAULT_TYPE,
    booking_id: int,
) -> None:
    """Отправляет администраторам уведомление о новой заявке."""
    admin_ids = context.application.bot_data.get("admin_telegram_ids", frozenset())
    session_factory = get_session_factory(context)

    if not admin_ids or session_factory is None:
        return

    with session_factory() as session:
        booking = get_booking_by_id(session, booking_id)

        if booking is None:
            return

        room_name = get_room_name_for_booking(session, booking)

    message_text = format_admin_booking_message(booking, room_name)
    keyboard = build_booking_review_keyboard(booking.id)

    for admin_id in admin_ids:
        await context.bot.send_message(
            chat_id=int(admin_id),
            text=message_text,
            reply_markup=keyboard,
        )


async def _notify_user_about_review(
    context: ContextTypes.DEFAULT_TYPE,
    user_telegram_id: str | None,
    booking_id: int,
    *,
    approved: bool,
) -> None:
    """Уведомляет пользователя о решении администратора."""
    if user_telegram_id is None:
        return

    if approved:
        message = format_user_approved_message(booking_id)
    else:
        message = format_user_rejected_message(booking_id)

    await context.bot.send_message(chat_id=int(user_telegram_id), text=message)


async def _process_booking_review(
    context: ContextTypes.DEFAULT_TYPE,
    booking_id: int,
    *,
    approved: bool,
) -> str:
    """Одобряет или отклоняет заявку и уведомляет пользователя."""
    session_factory = get_session_factory(context)

    if session_factory is None:
        return _("Ошибка настройки бота: не удалось подключиться к базе данных.")

    with session_factory() as session:
        if approved:
            result = approve_booking(session, booking_id)
        else:
            result = reject_booking(session, booking_id)

    if result.success:
        await _notify_user_about_review(
            context,
            result.user_telegram_id,
            booking_id,
            approved=approved,
        )

    return result.message


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /admin."""
    if update.message is None:
        return

    if not await _ensure_admin(update, context):
        return

    await update.message.reply_text(get_admin_command_usage())


async def pending_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /pending."""
    if update.message is None:
        return

    if not await _ensure_admin(update, context):
        return

    session_factory = get_session_factory(context)

    if session_factory is None:
        await update.message.reply_text(
            _("Ошибка настройки бота: не удалось подключиться к базе данных.")
        )
        return

    with session_factory() as session:
        bookings = get_pending_bookings(session)
        room_names = get_room_names_for_bookings(session, bookings)

    await update.message.reply_text(
        format_pending_bookings_message(bookings, room_names)
    )


async def approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /approve."""
    if update.message is None:
        return

    if not await _ensure_admin(update, context):
        return

    try:
        booking_id = parse_booking_id_request(context.args, "approve")
    except ValueError as error:
        await update.message.reply_text(str(error))
        return

    message = await _process_booking_review(context, booking_id, approved=True)
    await update.message.reply_text(message)


async def reject_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /reject."""
    if update.message is None:
        return

    if not await _ensure_admin(update, context):
        return

    try:
        booking_id = parse_booking_id_request(context.args, "reject")
    except ValueError as error:
        await update.message.reply_text(str(error))
        return

    message = await _process_booking_review(context, booking_id, approved=False)
    await update.message.reply_text(message)


async def booking_review_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Обрабатывает нажатия кнопок «Одобрить» и «Отклонить»."""
    query = update.callback_query

    if query is None:
        return

    user = update.effective_user

    if user is None:
        await query.answer()
        return

    activate_user_locale(context, str(user.id), user.language_code)

    if not is_admin(context, str(user.id)):
        await query.answer(_("Эта команда доступна только администраторам."), show_alert=True)
        return

    if query.data is None:
        await query.answer()
        return

    try:
        action, booking_id = parse_review_callback_data(query.data)
    except ValueError as error:
        await query.answer(str(error), show_alert=True)
        return

    message = await _process_booking_review(
        context,
        booking_id,
        approved=action == "approve",
    )

    if query.message is not None:
        await query.message.edit_text(message)

    await query.answer()
