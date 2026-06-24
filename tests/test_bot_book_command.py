from datetime import date

import pytest

from roomkeeper.bot.book_command import (
    BookRoomRequest,
    parse_book_room_request,
)


def test_parse_book_room_request_minimal() -> None:
    """Проверяем минимальный вариант команды /book."""

    request = parse_book_room_request(
        ["605", "2026-06-22", "08:45", "10:20", "подготовка", "к", "защите"]
    )

    assert request == BookRoomRequest(
        room_name="605",
        booking_date=date(2026, 6, 22),
        start_time="08:45",
        end_time="10:20",
        purpose="подготовка к защите",
        week_type="all",
    )


def test_parse_book_room_request_with_week_type() -> None:
    """Проверяем команду /book с типом недели."""

    request = parse_book_room_request(
        ["605", "2026-06-22", "08:45", "10:20", "even", "подготовка"]
    )

    assert request == BookRoomRequest(
        room_name="605",
        booking_date=date(2026, 6, 22),
        start_time="08:45",
        end_time="10:20",
        purpose="подготовка",
        week_type="even",
    )


def test_parse_book_room_request_requires_arguments() -> None:
    """Проверяем, что без обязательных аргументов команда некорректна."""

    with pytest.raises(ValueError, match="Использование"):
        parse_book_room_request(["605"])


def test_parse_book_room_request_checks_date() -> None:
    """Проверяем ошибку при неправильной дате."""

    with pytest.raises(ValueError, match="Дата должна быть"):
        parse_book_room_request(
            ["605", "22.06.2026", "08:45", "10:20", "подготовка"]
        )


def test_parse_book_room_request_checks_time_order() -> None:
    """Проверяем, что начало должно быть раньше конца."""

    with pytest.raises(ValueError, match="Время начала"):
        parse_book_room_request(
            ["605", "2026-06-22", "10:20", "08:45", "подготовка"]
        )


def test_parse_book_room_request_requires_purpose_after_week_type() -> None:
    """Проверяем, что после типа недели всё равно нужна цель."""

    with pytest.raises(ValueError, match="цель"):
        parse_book_room_request(
            ["605", "2026-06-22", "08:45", "10:20", "odd"]
        )
