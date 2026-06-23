from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from roomkeeper.db.session import DEFAULT_DATABASE_URL


@dataclass(frozen=True)
class BotConfig:
    """Настройки Telegram-бота."""

    token: str
    database_url: str = DEFAULT_DATABASE_URL


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

    return BotConfig(
        token=token,
        database_url=database_url,
    )
