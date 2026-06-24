from datetime import date

import pytest

from roomkeeper.bot.user_bookings_command import (
    format_status,
    format_user_bookings_message,
    parse_cancel_booking_request,
)
from roomkeeper.db.models import Booking


def test_parse_cancel_booking_request() -> None:
    """Проверяем разбор команды отмены заявки."""

    assert parse_cancel_booking_request(["3"]) == 3


def test_parse_cancel_booking_request_requires_one_argument() -> None:
    """Проверяем, что нужен ровно один аргумент."""

    with pytest.raises(ValueError, match="Использование"):
        parse_cancel_booking_request([])

    with pytest.raises(ValueError, match="Использование"):
        parse_cancel_booking_request(["1", "2"])


def test_parse_cancel_booking_request_checks_integer() -> None:
    """Проверяем, что номер заявки должен быть числом."""

    with pytest.raises(ValueError, match="целым числом"):
        parse_cancel_booking_request(["abc"])


def test_parse_cancel_booking_request_checks_positive_number() -> None:
    """Проверяем, что номер заявки должен быть положительным."""

    with pytest.raises(ValueError, match="положительным"):
        parse_cancel_booking_request(["0"])


def test_format_status() -> None:
    """Проверяем перевод статусов в понятный текст."""

    assert format_status("pending") == "ожидает подтверждения"
    assert format_status("approved") == "подтверждена"
    assert format_status("rejected") == "отклонена"
    assert format_status("canceled") == "отменена"
    assert format_status("unknown") == "unknown"


def test_format_user_bookings_message_without_bookings() -> None:
    """Проверяем сообщение для пользователя без заявок."""

    message = format_user_bookings_message([], {})

    assert "пока нет заявок" in message
    assert "/book" in message


def test_format_user_bookings_message_with_bookings() -> None:
    """Проверяем сообщение со списком заявок."""

    booking = Booking(
        id=1,
        room_id=10,
        user_telegram_id="123",
        user_name="student",
        booking_date=date(2026, 6, 22),
        start_time="08:45",
        end_time="10:20",
        purpose="подготовка к защите",
        status="pending",
    )

    message = format_user_bookings_message(
        bookings=[booking],
        room_names={10: "605"},
    )

    assert "#1" in message
    assert "605" in message
    assert "2026-06-22" in message
    assert "08:45–10:20" in message
    assert "подготовка к защите" in message
    assert "ожидает подтверждения" in message
    assert "/cancel_booking" in message
