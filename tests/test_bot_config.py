import pytest

from roomkeeper.bot.config import BotConfig, load_bot_config


def test_load_bot_config_reads_environment(monkeypatch) -> None:
    """Проверяем, что настройки бота читаются из переменных окружения."""

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:test-token")
    monkeypatch.setenv("ROOMKEEPER_DATABASE_URL", "sqlite:///test.db")

    config = load_bot_config(load_env_file=False)

    assert config == BotConfig(
        token="123456:test-token",
        database_url="sqlite:///test.db",
        default_locale="ru",
    )


def test_load_bot_config_uses_default_database_url(monkeypatch) -> None:
    """Проверяем, что адрес БД можно не задавать явно."""

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:test-token")
    monkeypatch.delenv("ROOMKEEPER_DATABASE_URL", raising=False)

    config = load_bot_config(load_env_file=False)

    assert config.token == "123456:test-token"
    assert config.database_url == "sqlite:///data/roomkeeper.db"


def test_load_bot_config_requires_token(monkeypatch) -> None:
    """Проверяем, что без токена бот не запускается."""

    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("ROOMKEEPER_DATABASE_URL", raising=False)

    with pytest.raises(RuntimeError, match="TELEGRAM_BOT_TOKEN"):
        load_bot_config(load_env_file=False)
