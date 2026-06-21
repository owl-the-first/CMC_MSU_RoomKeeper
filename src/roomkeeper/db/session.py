from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


# адрес базы данных по умолчанию; SQLite-файл будет храниться в каталоге data
DEFAULT_DATABASE_URL = "sqlite:///data/roomkeeper.db"


def get_engine(database_url: str = DEFAULT_DATABASE_URL, echo: bool = False) -> Engine:
    """Создает подключение к базе данных."""
    # для SQLite создаем каталог, если он отсутствует
    if database_url.startswith("sqlite:///") and database_url != "sqlite:///:memory:":
        database_path = Path(database_url.removeprefix("sqlite:///"))

        # создаем родительский каталог для файла базы данных
        if database_path.parent != Path("."):
            database_path.parent.mkdir(parents=True, exist_ok=True)

    # создаем и возвращаем объект подключения
    return create_engine(database_url, echo=echo, future=True)


def get_session_factory(database_url: str = DEFAULT_DATABASE_URL) -> sessionmaker[Session]:
    """Создает фабрику сессий для работы с БД."""
    # создаем подключение к базе данных
    engine = get_engine(database_url)

    # создаем фабрику объектов Session
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )
