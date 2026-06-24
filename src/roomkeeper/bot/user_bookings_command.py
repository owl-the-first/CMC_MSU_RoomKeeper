from __future__ import annotations

from typing import Sequence

from roomkeeper.db.models import Booking


MAX_BOOKINGS_IN_MESSAGE = 10


def get_user_bookings_usage() -> str:
    """Возвращает подсказку по команде /my_bookings."""

    return (
        "Использование:\n"
        "/my_bookings — показать ваши последние заявки"
    )


def get_cancel_booking_usage() -> str:
    """Возвращает подсказку по команде /cancel_booking."""

    return (
        "Использование:\n"
        "/cancel_booking НОМЕР_ЗАЯВКИ\n\n"
        "Пример:\n"
        "/cancel_booking 3\n\n"
        "Также можно коротко:\n"
        "/cancel 3"
    )


def parse_cancel_booking_request(args: Sequence[str]) -> int:
    """Разбирает аргументы команды отмены бронирования."""

    if len(args) != 1:
        raise ValueError(get_cancel_booking_usage())

    try:
        booking_id = int(args[0])
    except ValueError as error:
        raise ValueError("Номер заявки должен быть целым числом.") from error

    if booking_id <= 0:
        raise ValueError("Номер заявки должен быть положительным числом.")

    return booking_id


def format_status(status: str) -> str:
    """Возвращает понятное описание статуса заявки."""

    status_names = {
        "pending": "ожидает подтверждения",
        "approved": "подтверждена",
        "rejected": "отклонена",
        "canceled": "отменена",
    }

    return status_names.get(status, status)


def format_user_bookings_message(
    bookings: list[Booking],
    room_names: dict[int, str],
) -> str:
    """Формирует сообщение со списком заявок пользователя."""

    if not bookings:
        return (
            "У вас пока нет заявок на бронирование.\n\n"
            "Чтобы создать заявку, используйте команду:\n"
            "/book АУДИТОРИЯ ДАТА НАЧАЛО КОНЕЦ ЦЕЛЬ"
        )

    visible_bookings = bookings[:MAX_BOOKINGS_IN_MESSAGE]
    hidden_count = len(bookings) - len(visible_bookings)

    lines = ["Ваши заявки:", ""]

    for booking in visible_bookings:
        room_name = room_names.get(booking.room_id, f"id={booking.room_id}")

        lines.extend(
            [
                f"#{booking.id}",
                f"Аудитория: {room_name}",
                f"Дата: {booking.booking_date.isoformat()}",
                f"Время: {booking.start_time}–{booking.end_time}",
                f"Цель: {booking.purpose}",
                f"Статус: {format_status(booking.status)}",
                "",
            ]
        )

    if hidden_count > 0:
        lines.append(f"И ещё {hidden_count} заявок.")

    lines.append("Чтобы отменить заявку, напишите:")
    lines.append("/cancel_booking НОМЕР_ЗАЯВКИ")

    return "\n".join(lines).strip()
