from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from roomkeeper.bot.admin_access import parse_admin_ids
from roomkeeper.db.session import DEFAULT_DATABASE_URL
from roomkeeper.i18n import DEFAULT_LOCALE, normalize_locale


@dataclass(frozen=True)
class BotConfig:
    """Настройки Telegram-бота."""

    token: str
    database_url: str = DEFAULT_DATABASE_URL
    default_locale: str = DEFAULT_LOCALE
    admin_telegram_ids: frozenset[str] = frozenset()


def load_bot_config(load_env_file: bool = True) -> BotConfig:
    """Загружает настройки бота из переменных окружения."""
    if load_env_file:
        load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

    if not token:
        raise RuntimeError(
            "Не задан TELEGRAM_BOT_TOKEN. "
            "Создайте файл .env по примеру .env.example."
        )

    database_url = os.getenv("ROOMKEEPER_DATABASE_URL", DEFAULT_DATABASE_URL).strip()

    if not database_url:
        database_url = DEFAULT_DATABASE_URL

    default_locale = normalize_locale(
        os.getenv("ROOMKEEPER_DEFAULT_LOCALE", DEFAULT_LOCALE)
    )

    admin_telegram_ids = parse_admin_ids(os.getenv("TELEGRAM_ADMIN_IDS", ""))

    return BotConfig(
        token=token,
        database_url=database_url,
        default_locale=default_locale,
        admin_telegram_ids=admin_telegram_ids,
    )
