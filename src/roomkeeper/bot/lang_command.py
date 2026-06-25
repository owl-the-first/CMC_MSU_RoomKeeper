from __future__ import annotations

from typing import Sequence

from roomkeeper.i18n import SUPPORTED_LOCALES, _, get_locale


def get_lang_command_usage() -> str:
    """Возвращает подсказку по команде /lang."""
    return (
        _("Использование:\n")
        + "/lang ru — русский язык\n"
        + "/lang en — English\n\n"
        + _("Поддерживаемые локали: {locales}").format(
            locales=", ".join(sorted(SUPPORTED_LOCALES))
        )
    )


def parse_lang_request(args: Sequence[str]) -> str:
    """Разбирает аргументы команды /lang."""
    if len(args) != 1:
        raise ValueError(get_lang_command_usage())

    locale = args[0].strip().lower()

    if locale not in SUPPORTED_LOCALES:
        raise ValueError(
            _("Локаль {locale!r} не поддерживается.").format(locale=locale)
            + "\n\n"
            + get_lang_command_usage()
        )

    return locale


def format_lang_changed_message(locale: str) -> str:
    """Формирует сообщение об успешной смене языка."""
    if locale == "en":
        return "Language changed to English."

    return "Язык изменён на русский."


def format_current_language_message() -> str:
    """Формирует сообщение о текущем языке интерфейса."""
    locale = get_locale()

    if locale == "en":
        return "Current language: English.\n\n" + get_lang_command_usage()

    return "Текущий язык: русский.\n\n" + get_lang_command_usage()
