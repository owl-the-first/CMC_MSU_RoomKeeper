from roomkeeper.db.init_db import create_tables
from roomkeeper.db.session import DEFAULT_DATABASE_URL


def main() -> None:
    """Создаёт таблицы базы данных."""
    # создаем все таблицы базы данных
    create_tables()
    # выводим адрес созданной базы данных
    print(f"Database initialized: {DEFAULT_DATABASE_URL}")


if __name__ == "__main__":
    main()
