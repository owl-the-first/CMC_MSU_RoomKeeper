from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Sequence

from roomkeeper.bot.free_command import VALID_WEEK_TYPES
from roomkeeper.search.free_rooms import time_to_minutes


@dataclass(frozen=True)
class BookRoomRequest:
    """Данные, которые пользователь ввёл в команде /book."""

    room_name: str
    booking_date: date
    start_time: str
    end_time: str
    purpose: str
    week_type: str = "all"


def get_book_command_usage() -> str:
    """Возвращает подсказку по использованию команды /book."""

    return (
        "Использование:\n"
        "/book АУДИТОРИЯ ДАТА НАЧАЛО КОНЕЦ [ТИП_НЕДЕЛИ] ЦЕЛЬ\n\n"
        "Примеры:\n"
        "/book 605 2026-06-22 08:45 10:20 подготовка к защите\n"
        "/book 605 2026-06-22 08:45 10:20 even подготовка к защите\n"
        "/book П-13 2026-06-22 12:50 14:25 odd встреча команды\n\n"
        "Тип недели необязателен:\n"
        "all — любая неделя\n"
        "even — чётная неделя\n"
        "odd — нечётная неделя"
    )


def parse_book_room_request(args: Sequence[str]) -> BookRoomRequest:
    """Разбирает аргументы команды /book."""

    if len(args) < 5:
        raise ValueError(get_book_command_usage())

    room_name = args[0].strip()

    if not room_name:
        raise ValueError("Нужно указать аудиторию.")

    try:
        booking_date = date.fromisoformat(args[1])
    except ValueError as error:
        raise ValueError(
            "Дата должна быть в формате YYYY-MM-DD, например 2026-06-22."
        ) from error

    start_time = args[2]
    end_time = args[3]

    try:
        start_minutes = time_to_minutes(start_time)
        end_minutes = time_to_minutes(end_time)
    except ValueError as error:
        raise ValueError(
            "Время должно быть в формате HH:MM, например 08:45."
        ) from error

    if start_minutes >= end_minutes:
        raise ValueError("Время начала должно быть меньше времени окончания.")

    week_type = "all"
    purpose_parts = list(args[4:])

    if purpose_parts and purpose_parts[0].lower() in VALID_WEEK_TYPES:
        week_type = purpose_parts[0].lower()
        purpose_parts = purpose_parts[1:]

    purpose = " ".join(purpose_parts).strip()

    if not purpose:
        raise ValueError("Нужно указать цель бронирования.")

    return BookRoomRequest(
        room_name=room_name,
        booking_date=booking_date,
        start_time=start_time,
        end_time=end_time,
        purpose=purpose,
        week_type=week_type,
    )
