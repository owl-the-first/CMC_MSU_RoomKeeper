from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Sequence

from roomkeeper.search.free_rooms import RoomAvailability, time_to_minutes

VALID_WEEK_TYPES = {"all", "even", "odd"}
MAX_ROOMS_IN_MESSAGE = 30


@dataclass(frozen=True)
class FreeRoomsRequest:
    """Данные, которые пользователь ввёл в команде /free."""

    booking_date: date
    start_time: str
    end_time: str
    week_type: str = "all"
    room_query: str | None = None


def get_free_command_usage() -> str:
    """Возвращает подсказку по использованию команды /free."""

    return (
        "Использование:\n"
        "/free ДАТА НАЧАЛО КОНЕЦ [ТИП_НЕДЕЛИ] [АУДИТОРИЯ]\n\n"
        "Примеры:\n"
        "/free 2026-06-22 08:45 10:20\n"
        "/free 2026-06-22 08:45 10:20 even\n"
        "/free 2026-06-22 08:45 10:20 odd\n"
        "/free 2026-06-22 08:45 10:20 605\n"
        "/free 2026-06-22 08:45 10:20 even 605\n\n"
        "Тип недели:\n"
        "all — любая неделя\n"
        "even — чётная неделя\n"
        "odd — нечётная неделя"
    )


def parse_free_rooms_request(args: Sequence[str]) -> FreeRoomsRequest:
    """Разбирает аргументы команды /free."""

    if len(args) < 3:
        raise ValueError(get_free_command_usage())

    try:
        booking_date = date.fromisoformat(args[0])
    except ValueError as error:
        raise ValueError(
            "Дата должна быть в формате YYYY-MM-DD, например 2026-06-22."
        ) from error

    start_time = args[1]
    end_time = args[2]

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
    room_query = None

    extra_args = list(args[3:])

    if extra_args:
        first_extra_arg = extra_args[0].lower()

        if first_extra_arg in VALID_WEEK_TYPES:
            week_type = first_extra_arg
            room_query_parts = extra_args[1:]
        else:
            room_query_parts = extra_args

        if room_query_parts:
            room_query = " ".join(room_query_parts)

    return FreeRoomsRequest(
        booking_date=booking_date,
        start_time=start_time,
        end_time=end_time,
        week_type=week_type,
        room_query=room_query,
    )


def format_free_rooms_message(
    request: FreeRoomsRequest,
    rooms: list[RoomAvailability],
) -> str:
    """Формирует сообщение со списком свободных аудиторий."""

    if not rooms:
        return (
            "Свободные аудитории не найдены.\n\n"
            f"Дата: {request.booking_date.isoformat()}\n"
            f"Время: {request.start_time}–{request.end_time}\n"
            f"Тип недели: {request.week_type}"
        )

    visible_rooms = rooms[:MAX_ROOMS_IN_MESSAGE]
    hidden_count = len(rooms) - len(visible_rooms)

    lines = [
        "Свободные аудитории:",
        "",
        f"Дата: {request.booking_date.isoformat()}",
        f"Время: {request.start_time}–{request.end_time}",
        f"Тип недели: {request.week_type}",
    ]

    if request.room_query:
        lines.append(f"Фильтр: {request.room_query}")

    lines.append("")

    for room in visible_rooms:
        lines.append(f"• {room.room_name}")

    if hidden_count > 0:
        lines.append("")
        lines.append(f"И ещё {hidden_count} аудиторий.")

    return "\n".join(lines)
