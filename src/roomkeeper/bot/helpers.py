from __future__ import annotations

from telegram.ext import ContextTypes

from roomkeeper.bot.locale import resolve_user_locale
from roomkeeper.i18n import set_locale


def get_session_factory(context: ContextTypes.DEFAULT_TYPE):
    """Достаёт фабрику сессий БД из данных приложения."""
    return context.application.bot_data.get("session_factory")


def activate_user_locale(
    context: ContextTypes.DEFAULT_TYPE,
    user_telegram_id: str | None,
    language_code: str | None = None,
) -> None:
    """Устанавливает локаль для текущего запроса пользователя."""
    set_locale(
        resolve_user_locale(
            context=context,
            user_telegram_id=user_telegram_id,
            language_code=language_code,
        )
    )
