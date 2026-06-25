from __future__ import annotations

from telegram.ext import ContextTypes


def parse_admin_ids(raw_value: str) -> frozenset[str]:
    """Разбирает список Telegram ID администраторов из переменной окружения."""
    admin_ids: set[str] = set()

    for part in raw_value.split(","):
        admin_id = part.strip()

        if admin_id:
            admin_ids.add(admin_id)

    return frozenset(admin_ids)


def get_admin_ids(context: ContextTypes.DEFAULT_TYPE) -> frozenset[str]:
    """Возвращает Telegram ID администраторов из настроек бота."""
    admin_ids = context.application.bot_data.get("admin_telegram_ids", frozenset())

    if isinstance(admin_ids, frozenset):
        return admin_ids

    return frozenset(admin_ids)


def is_admin(context: ContextTypes.DEFAULT_TYPE, user_telegram_id: str | None) -> bool:
    """Проверяет, является ли пользователь администратором."""
    if user_telegram_id is None:
        return False

    return user_telegram_id in get_admin_ids(context)
