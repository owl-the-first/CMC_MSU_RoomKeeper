from __future__ import annotations

from telegram.ext import ContextTypes

from roomkeeper.i18n import DEFAULT_LOCALE, SUPPORTED_LOCALES, normalize_locale

USER_LOCALES_KEY = "user_locales"


def get_user_locales_store(context: ContextTypes.DEFAULT_TYPE) -> dict[str, str]:
    """Возвращает хранилище выбранных пользователями локалей."""
    return context.application.bot_data.setdefault(USER_LOCALES_KEY, {})


def get_default_locale(context: ContextTypes.DEFAULT_TYPE) -> str:
    """Возвращает локаль по умолчанию из настроек бота."""
    return normalize_locale(context.application.bot_data.get("default_locale", DEFAULT_LOCALE))


def set_user_locale(
    context: ContextTypes.DEFAULT_TYPE,
    user_telegram_id: str,
    locale: str,
) -> str:
    """Сохраняет выбранную пользователем локаль."""
    normalized_locale = normalize_locale(locale)
    get_user_locales_store(context)[user_telegram_id] = normalized_locale
    return normalized_locale


def resolve_user_locale(
    context: ContextTypes.DEFAULT_TYPE,
    user_telegram_id: str | None,
    language_code: str | None = None,
) -> str:
    """Определяет локаль пользователя: выбор, язык Telegram или значение по умолчанию."""
    if user_telegram_id is not None:
        stored_locale = get_user_locales_store(context).get(user_telegram_id)

        if stored_locale is not None:
            return normalize_locale(stored_locale)

    if language_code:
        code = language_code.strip().lower().replace("_", "-").split("-", maxsplit=1)[0]

        if code in SUPPORTED_LOCALES:
            return code

    return get_default_locale(context)
