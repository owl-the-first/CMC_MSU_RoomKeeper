from datetime import date

import pytest

from roomkeeper.bot.free_command import FreeRoomsRequest, format_free_rooms_message
from roomkeeper.bot.lang_command import (
    format_lang_changed_message,
    parse_lang_request,
)
from roomkeeper.bot.locale import resolve_user_locale, set_user_locale
from roomkeeper.bot.user_bookings_command import format_status
from roomkeeper.i18n import (
    DEFAULT_LOCALE,
    SUPPORTED_LOCALES,
    get_locale,
    normalize_locale,
    set_locale,
)
from roomkeeper.search.free_rooms import RoomAvailability


class DummyApplication:
    def __init__(self, default_locale: str = "ru") -> None:
        self.bot_data: dict[str, object] = {"default_locale": default_locale}


class DummyContext:
    def __init__(self, default_locale: str = "ru") -> None:
        self.application = DummyApplication(default_locale=default_locale)


def test_normalize_locale_supports_aliases() -> None:
    """Проверяем нормализацию кодов языка."""
    assert normalize_locale("ru") == "ru"
    assert normalize_locale("en") == "en"
    assert normalize_locale("en-US") == "en"
    assert normalize_locale("ru_RU") == "ru"
    assert normalize_locale("de") == DEFAULT_LOCALE
    assert normalize_locale(None) == DEFAULT_LOCALE


def test_supported_locales_contains_ru_and_en() -> None:
    """Проверяем, что проект поддерживает как минимум две локали."""
    assert SUPPORTED_LOCALES == frozenset({"ru", "en"})


def test_russian_locale_returns_russian_bot_text() -> None:
    """Проверяем русские тексты бота."""
    set_locale("ru")

    assert get_locale() == "ru"
    assert format_status("pending") == "ожидает подтверждения"


def test_english_locale_returns_english_bot_text() -> None:
    """Проверяем английские тексты бота."""
    set_locale("en")

    assert get_locale() == "en"
    assert format_status("pending") == "pending approval"
    assert format_status("approved") == "approved"


def test_format_free_rooms_message_in_english() -> None:
    """Проверяем локализацию ответа команды /free."""
    set_locale("en")

    request = FreeRoomsRequest(
        booking_date=date(2026, 6, 22),
        start_time="08:45",
        end_time="10:20",
    )
    rooms = [RoomAvailability(room_id=1, room_name="605", is_free=True)]

    message = format_free_rooms_message(request, rooms)

    assert "Free rooms:" in message
    assert "605" in message


def test_format_free_rooms_message_in_russian() -> None:
    """Проверяем русский ответ команды /free."""
    set_locale("ru")

    request = FreeRoomsRequest(
        booking_date=date(2026, 6, 22),
        start_time="08:45",
        end_time="10:20",
    )

    message = format_free_rooms_message(request, [])

    assert "Свободные аудитории не найдены" in message


def test_parse_lang_request_accepts_supported_locales() -> None:
    """Проверяем разбор команды /lang."""
    assert parse_lang_request(["ru"]) == "ru"
    assert parse_lang_request(["en"]) == "en"


def test_parse_lang_request_rejects_unknown_locale() -> None:
    """Проверяем ошибку для неподдерживаемой локали."""
    with pytest.raises(ValueError, match="не поддерживается"):
        parse_lang_request(["de"])


def test_format_lang_changed_message() -> None:
    """Проверяем сообщения о смене языка."""
    assert "русский" in format_lang_changed_message("ru")
    assert "English" in format_lang_changed_message("en")


def test_resolve_user_locale_uses_saved_choice() -> None:
    """Проверяем сохранение выбранной пользователем локали."""
    context = DummyContext(default_locale="ru")

    set_user_locale(context, "42", "en")

    assert resolve_user_locale(context, "42", language_code="ru") == "en"


def test_resolve_user_locale_uses_telegram_language_code() -> None:
    """Проверяем выбор локали по языку Telegram."""
    context = DummyContext(default_locale="ru")

    assert resolve_user_locale(context, "42", language_code="en") == "en"


def test_resolve_user_locale_falls_back_to_default() -> None:
    """Проверяем локаль по умолчанию."""
    context = DummyContext(default_locale="en")

    assert resolve_user_locale(context, "42", language_code="de") == "en"
