from datetime import date

import pytest

from roomkeeper.bot.free_command import (
    FreeRoomsRequest,
    format_free_rooms_message,
    parse_free_rooms_request,
)
from roomkeeper.search.free_rooms import RoomAvailability


def test_parse_free_rooms_request_minimal() -> None:
    """Проверяем минимальный вариант команды /free."""

    request = parse_free_rooms_request(["2026-06-22", "08:45", "10:20"])

    assert request == FreeRoomsRequest(
        booking_date=date(2026, 6, 22),
        start_time="08:45",
        end_time="10:20",
        week_type="all",
        room_query=None,
    )


def test_parse_free_rooms_request_with_week_type() -> None:
    """Проверяем команду /free с типом недели."""

    request = parse_free_rooms_request(["2026-06-22", "08:45", "10:20", "even"])

    assert request == FreeRoomsRequest(
        booking_date=date(2026, 6, 22),
        start_time="08:45",
        end_time="10:20",
        week_type="even",
        room_query=None,
    )


def test_parse_free_rooms_request_with_room() -> None:
    """Проверяем команду /free с фильтром по аудитории."""

    request = parse_free_rooms_request(["2026-06-22", "08:45", "10:20", "605"])

    assert request == FreeRoomsRequest(
        booking_date=date(2026, 6, 22),
        start_time="08:45",
        end_time="10:20",
        week_type="all",
        room_query="605",
    )


def test_parse_free_rooms_request_with_week_type_and_room() -> None:
    """Проверяем команду /free с типом недели и аудиторией."""

    request = parse_free_rooms_request(
        ["2026-06-22", "08:45", "10:20", "odd", "П-13"]
    )

    assert request == FreeRoomsRequest(
        booking_date=date(2026, 6, 22),
        start_time="08:45",
        end_time="10:20",
        week_type="odd",
        room_query="П-13",
    )


def test_parse_free_rooms_request_requires_arguments() -> None:
    """Проверяем, что без аргументов команда считается некорректной."""

    with pytest.raises(ValueError, match="Использование"):
        parse_free_rooms_request([])


def test_parse_free_rooms_request_checks_date() -> None:
    """Проверяем ошибку при неправильной дате."""

    with pytest.raises(ValueError, match="Дата должна быть"):
        parse_free_rooms_request(["22.06.2026", "08:45", "10:20"])


def test_parse_free_rooms_request_checks_time_order() -> None:
    """Проверяем, что начало должно быть раньше конца."""

    with pytest.raises(ValueError, match="Время начала"):
        parse_free_rooms_request(["2026-06-22", "10:20", "08:45"])


def test_format_free_rooms_message_with_rooms() -> None:
    """Проверяем форматирование ответа со свободными аудиториями."""

    request = FreeRoomsRequest(
        booking_date=date(2026, 6, 22),
        start_time="08:45",
        end_time="10:20",
    )

    rooms = [
        RoomAvailability(room_id=1, room_name="605", is_free=True),
        RoomAvailability(room_id=2, room_name="731", is_free=True),
    ]

    message = format_free_rooms_message(request, rooms)

    assert "Свободные аудитории" in message
    assert "605" in message
    assert "731" in message
    assert "2026-06-22" in message


def test_format_free_rooms_message_without_rooms() -> None:
    """Проверяем форматирование ответа, когда аудиторий нет."""

    request = FreeRoomsRequest(
        booking_date=date(2026, 6, 22),
        start_time="08:45",
        end_time="10:20",
    )

    message = format_free_rooms_message(request, [])

    assert "Свободные аудитории не найдены" in message
    assert "2026-06-22" in message
