from sqlalchemy import Engine

from roomkeeper.db.models import Base
from roomkeeper.db.session import DEFAULT_DATABASE_URL, get_engine


def create_tables(database_url: str = DEFAULT_DATABASE_URL) -> Engine:
    """Создает таблицы в базе данных."""
    engine = get_engine(database_url)       # создаем подключение к базе данных
    Base.metadata.create_all(engine)        # создаем все таблицы, описанные в моделях

    return engine       # возвращаем объект подключения


def reset_tables(database_url: str = DEFAULT_DATABASE_URL) -> Engine:
    """Удаляет и заново создает все таблицы."""
    engine = get_engine(database_url)       # создаем подключение к базе данных
    Base.metadata.drop_all(engine)          # удаляем существующие таблицы
    Base.metadata.create_all(engine)        # создаем таблицы заново

    return engine       # возвращаем объект подключения
