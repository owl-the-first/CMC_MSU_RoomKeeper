from __future__ import annotations

from typing import Sequence

from roomkeeper.db.models import Booking
from roomkeeper.i18n import _, ngettext

MAX_BOOKINGS_IN_MESSAGE = 10


def get_user_bookings_usage() -> str:
    """Возвращает подсказку по команде /my_bookings."""
    return (
        _("Использование:\n")
        + "/my_bookings — "
        + _("показать ваши последние заявки")
    )


def get_cancel_booking_usage() -> str:
    """Возвращает подсказку по команде /cancel_booking."""
    return (
        _("Использование:\n")
        + "/cancel_booking НОМЕР_ЗАЯВКИ\n\n"
        + _("Пример:\n")
        + "/cancel_booking 3\n\n"
        + _("Также можно коротко:\n")
        + "/cancel 3"
    )


def parse_cancel_booking_request(args: Sequence[str]) -> int:
    """Разбирает аргументы команды отмены бронирования."""
    if len(args) != 1:
        raise ValueError(get_cancel_booking_usage())

    try:
        booking_id = int(args[0])
    except ValueError as error:
        raise ValueError(_("Номер заявки должен быть целым числом.")) from error

    if booking_id <= 0:
        raise ValueError(_("Номер заявки должен быть положительным числом."))

    return booking_id


def format_status(status: str) -> str:
    """Возвращает понятное описание статуса заявки."""
    status_names = {
        "pending": _("ожидает подтверждения"),
        "approved": _("подтверждена"),
        "rejected": _("отклонена"),
        "canceled": _("отменена"),
    }

    return status_names.get(status, status)


def format_user_bookings_message(
    bookings: list[Booking],
    room_names: dict[int, str],
) -> str:
    """Формирует сообщение со списком заявок пользователя."""
    if not bookings:
        return (
            _("У вас пока нет заявок на бронирование.")
            + "\n\n"
            + _("Чтобы создать заявку, используйте команду:\n")
            + "/book АУДИТОРИЯ ДАТА НАЧАЛО КОНЕЦ ЦЕЛЬ"
        )

    visible_bookings = bookings[:MAX_BOOKINGS_IN_MESSAGE]
    hidden_count = len(bookings) - len(visible_bookings)

    lines = [_("Ваши заявки:"), ""]

    for booking in visible_bookings:
        room_name = room_names.get(booking.room_id, f"id={booking.room_id}")

        lines.extend(
            [
                f"#{booking.id}",
                _("Аудитория: {room_name}").format(room_name=room_name),
                _("Дата: {date}").format(date=booking.booking_date.isoformat()),
                _("Время: {start}–{end}").format(
                    start=booking.start_time,
                    end=booking.end_time,
                ),
                _("Цель: {purpose}").format(purpose=booking.purpose),
                _("Статус: {status}").format(status=format_status(booking.status)),
                "",
            ]
        )

    if hidden_count > 0:
        lines.append(
            ngettext(
                "И ещё {count} заявка.",
                "И ещё {count} заявок.",
                hidden_count,
            ).format(count=hidden_count)
        )

    lines.append(_("Чтобы отменить заявку, напишите:"))
    lines.append("/cancel_booking НОМЕР_ЗАЯВКИ")

    return "\n".join(lines).strip()
