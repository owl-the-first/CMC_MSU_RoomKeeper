"""Интернационализация на основе gettext и Babel."""

from __future__ import annotations

from contextvars import ContextVar
from functools import lru_cache
from gettext import GNUTranslations, NullTranslations
from importlib.resources import files

SUPPORTED_LOCALES = frozenset({"ru", "en"})
DEFAULT_LOCALE = "ru"

_current_locale: ContextVar[str] = ContextVar("current_locale", default=DEFAULT_LOCALE)


def normalize_locale(locale: str | None) -> str:
    """Приводит код языка к поддерживаемой локали."""
    if not locale:
        return DEFAULT_LOCALE

    code = locale.strip().lower().replace("_", "-").split("-", maxsplit=1)[0]

    if code in SUPPORTED_LOCALES:
        return code

    return DEFAULT_LOCALE


def get_locale() -> str:
    """Возвращает текущую локаль из контекста."""
    return normalize_locale(_current_locale.get())


def set_locale(locale: str) -> None:
    """Устанавливает текущую локаль для контекста выполнения."""
    _current_locale.set(normalize_locale(locale))


@lru_cache(maxsize=len(SUPPORTED_LOCALES))
def _load_translations(locale: str) -> GNUTranslations | NullTranslations:
    """Загружает и кэширует переводы для локали."""
    from gettext import translation

    localedir = files("roomkeeper") / "locales"

    return translation(
        domain="messages",
        localedir=str(localedir),
        languages=[locale],
        fallback=True,
    )


def gettext(message: str) -> str:
    """Возвращает перевод строки для текущей локали."""
    return _load_translations(get_locale()).gettext(message)


def ngettext(singular: str, plural: str, n: int) -> str:
    """Возвращает перевод с учётом числительного для текущей локали."""
    return _load_translations(get_locale()).ngettext(singular, plural, n)


_ = gettext
