from datetime import date

import pytest

from roomkeeper.bot.admin_access import is_admin, parse_admin_ids
from roomkeeper.bot.admin_command import (
    build_booking_review_keyboard,
    format_admin_booking_message,
    format_pending_bookings_message,
    format_user_display,
    parse_booking_id_request,
    parse_review_callback_data,
)
from roomkeeper.db.models import Booking


class DummyApplication:
    def __init__(self, admin_ids: frozenset[str]) -> None:
        self.bot_data = {"admin_telegram_ids": admin_ids}


class DummyContext:
    def __init__(self, admin_ids: frozenset[str]) -> None:
        self.application = DummyApplication(admin_ids)


def test_parse_admin_ids() -> None:
    """Проверяем разбор списка администраторов."""

    assert parse_admin_ids("123, 456") == frozenset({"123", "456"})
    assert parse_admin_ids("") == frozenset()


def test_is_admin() -> None:
    """Проверяем определение администратора."""

    context = DummyContext(frozenset({"123"}))

    assert is_admin(context, "123")
    assert not is_admin(context, "456")
    assert not is_admin(context, None)


def test_format_admin_booking_message() -> None:
    """Проверяем карточку заявки для администратора."""

    booking = Booking(
        id=12,
        room_id=1,
        user_telegram_id="999",
        user_name="username",
        booking_date=date(2026, 2, 20),
        start_time="12:50",
        end_time="14:25",
        purpose="встреча проектной команды",
        status="pending",
    )

    message = format_admin_booking_message(booking, "605")

    assert "#12" in message
    assert "605" in message
    assert "20.02.2026" in message
    assert "12:50–14:25" in message
    assert "@username" in message
    assert "встреча проектной команды" in message


def test_format_user_display_adds_at_sign_for_username() -> None:
    """Проверяем форматирование username."""

    assert format_user_display("username", "123") == "@username"
    assert format_user_display("@username", "123") == "@username"
    assert format_user_display("Иван Иванов", "123") == "Иван Иванов"


def test_build_booking_review_keyboard() -> None:
    """Проверяем кнопки одобрения и отклонения."""

    keyboard = build_booking_review_keyboard(12)

    assert len(keyboard.inline_keyboard) == 1
    assert len(keyboard.inline_keyboard[0]) == 2
    assert keyboard.inline_keyboard[0][0].callback_data == "approve:12"
    assert keyboard.inline_keyboard[0][1].callback_data == "reject:12"


def test_parse_booking_id_request() -> None:
    """Проверяем разбор номера заявки."""

    assert parse_booking_id_request(["12"], "approve") == 12

    with pytest.raises(ValueError, match="Использование"):
        parse_booking_id_request([], "approve")


def test_parse_review_callback_data() -> None:
    """Проверяем разбор callback-данных кнопок."""

    assert parse_review_callback_data("approve:12") == ("approve", 12)
    assert parse_review_callback_data("reject:7") == ("reject", 7)

    with pytest.raises(ValueError):
        parse_review_callback_data("unknown:12")


def test_format_pending_bookings_message_without_bookings() -> None:
    """Проверяем сообщение при пустой очереди."""

    message = format_pending_bookings_message([], {})

    assert "Нет заявок" in message
