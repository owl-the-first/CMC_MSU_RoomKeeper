from __future__ import annotations

from typing import Sequence

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from roomkeeper.db.models import Booking
from roomkeeper.i18n import _

APPROVE_CALLBACK_PREFIX = "approve:"
REJECT_CALLBACK_PREFIX = "reject:"


def get_admin_command_usage() -> str:
    """Возвращает подсказку по админ-командам."""
    return (
        _("Админ-команды:\n")
        + "/admin — "
        + _("показать эту справку")
        + "\n"
        + "/pending — "
        + _("показать заявки, ожидающие решения")
        + "\n"
        + "/approve НОМЕР — "
        + _("подтвердить заявку")
        + "\n"
        + "/reject НОМЕР — "
        + _("отклонить заявку")
    )


def parse_booking_id_request(args: Sequence[str], command_name: str) -> int:
    """Разбирает номер заявки из аргументов админ-команды."""
    if len(args) != 1:
        raise ValueError(
            _("Использование:\n")
            + f"/{command_name} НОМЕР_ЗАЯВКИ\n\n"
            + _("Пример:\n")
            + f"/{command_name} 12"
        )

    try:
        booking_id = int(args[0])
    except ValueError as error:
        raise ValueError(_("Номер заявки должен быть целым числом.")) from error

    if booking_id <= 0:
        raise ValueError(_("Номер заявки должен быть положительным числом."))

    return booking_id


def format_user_display(user_name: str | None, user_telegram_id: str) -> str:
    """Форматирует имя пользователя для сообщения администратору."""
    if not user_name:
        return user_telegram_id

    if user_name.startswith("@"):
        return user_name

    if " " not in user_name:
        return f"@{user_name}"

    return user_name


def format_booking_date(booking_date) -> str:
    """Форматирует дату заявки для админ-сообщения."""
    return booking_date.strftime("%d.%m.%Y")


def format_admin_booking_message(
    booking: Booking,
    room_name: str,
) -> str:
    """Формирует карточку заявки для администратора."""
    return "\n".join(
        [
            _("Заявка #{booking_id}").format(booking_id=booking.id),
            _("Аудитория: {room_name}").format(room_name=room_name),
            _("Дата: {booking_date}").format(
                booking_date=format_booking_date(booking.booking_date)
            ),
            _("Время: {start}–{end}").format(
                start=booking.start_time,
                end=booking.end_time,
            ),
            _("Пользователь: {user}").format(
                user=format_user_display(booking.user_name, booking.user_telegram_id)
            ),
            _("Цель: {purpose}").format(purpose=booking.purpose),
        ]
    )


def build_booking_review_keyboard(booking_id: int) -> InlineKeyboardMarkup:
    """Создаёт кнопки одобрения и отклонения заявки."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    _("Одобрить"),
                    callback_data=f"{APPROVE_CALLBACK_PREFIX}{booking_id}",
                ),
                InlineKeyboardButton(
                    _("Отклонить"),
                    callback_data=f"{REJECT_CALLBACK_PREFIX}{booking_id}",
                ),
            ]
        ]
    )


def format_pending_bookings_message(
    bookings: list[Booking],
    room_names: dict[int, str],
) -> str:
    """Формирует список заявок, ожидающих решения."""
    if not bookings:
        return _("Нет заявок, ожидающих решения.")

    lines = [_("Заявки, ожидающие решения:"), ""]

    for booking in bookings:
        room_name = room_names.get(booking.room_id, f"id={booking.room_id}")
        lines.append(format_admin_booking_message(booking, room_name))
        lines.append("")

    return "\n".join(lines).strip()


def format_user_approved_message(booking_id: int) -> str:
    """Формирует уведомление пользователю об одобрении заявки."""
    return _("Ваша заявка №{booking_id} подтверждена.").format(booking_id=booking_id)


def format_user_rejected_message(booking_id: int) -> str:
    """Формирует уведомление пользователю об отклонении заявки."""
    return _("Ваша заявка №{booking_id} отклонена.").format(booking_id=booking_id)


def parse_review_callback_data(callback_data: str) -> tuple[str, int]:
    """Разбирает callback-данные кнопок одобрения или отклонения."""
    if callback_data.startswith(APPROVE_CALLBACK_PREFIX):
        action = "approve"
        raw_booking_id = callback_data.removeprefix(APPROVE_CALLBACK_PREFIX)
    elif callback_data.startswith(REJECT_CALLBACK_PREFIX):
        action = "reject"
        raw_booking_id = callback_data.removeprefix(REJECT_CALLBACK_PREFIX)
    else:
        raise ValueError(_("Неизвестное действие администратора."))

    try:
        booking_id = int(raw_booking_id)
    except ValueError as error:
        raise ValueError(_("Некорректный номер заявки.")) from error

    if booking_id <= 0:
        raise ValueError(_("Некорректный номер заявки."))

    return action, booking_id
