import json
from dataclasses import dataclass
from pathlib import Path

from roomkeeper.db.init_db import create_tables
from roomkeeper.db.repository import (
    add_schedule_slot,
    clear_schedule_slots,
    count_rooms,
    count_schedule_slots,
)
from roomkeeper.db.session import DEFAULT_DATABASE_URL, get_session_factory


# путь к JSON-файлу с распарсенным расписанием
DEFAULT_SCHEDULE_JSON = Path("data/parsed/schedule_slots.json")


# результат импорта расписания в базу данных; используется для вывода статистики
@dataclass(frozen=True)
class ImportResult:
    """Результат импорта расписания в БД."""

    imported_slots: int             # количество импортированных записей
    rooms_count: int                # количество аудиторий в базе данных
    schedule_slots_count: int       # количество записей расписания в базе данных


def load_schedule_json(path: Path = DEFAULT_SCHEDULE_JSON) -> list[dict]:
    """Загружает JSON с расписанием."""
    # открываем JSON-файл
    with path.open(encoding="utf-8") as file:
        data = json.load(file)

    # проверяем, что верхний уровень является списком
    if not isinstance(data, list):
        raise ValueError("Schedule JSON must contain a list")

    # возвращаем данные
    return data


def import_schedule_slots(
    json_path: Path = DEFAULT_SCHEDULE_JSON,
    database_url: str = DEFAULT_DATABASE_URL,
) -> ImportResult:
    """Импортирует занятость аудиторий из JSON в базу данных."""
    # проверяем существование JSON-файла
    if not json_path.exists():
        raise FileNotFoundError(f"Schedule JSON not found: {json_path}")

    create_tables(database_url)         # создаем таблицы базы данных

    data = load_schedule_json(json_path)                    # загружаем данные из JSON
    session_factory = get_session_factory(database_url)     # создаем фабрику сессий

    imported_slots = 0                  # счетчик импортированных записей

    # открываем транзакцию
    with session_factory.begin() as session:
        clear_schedule_slots(session)           # удаляем старые записи расписания

        # последовательно импортируем записи
        for item in data:
            room_name = item.get("room")        # получаем название аудитории

            # пропускаем записи без аудитории
            if not room_name:
                continue

            # добавляем запись расписания в базу данных
            add_schedule_slot(
                session=session,
                room_name=room_name,
                weekday=item.get("weekday", ""),
                start_time=item.get("start_time", ""),
                end_time=item.get("end_time", ""),
                week_type=item.get("week_type", "all"),
                source=item.get("source_file", ""),
                raw_text=item.get("raw_line", ""),
            )

            imported_slots += 1                 # увеличиваем счетчик

    # открываем новую сессию для подсчета статистики
    with session_factory() as session:
        rooms_count = count_rooms(session)
        schedule_slots_count = count_schedule_slots(session)

    # возвращаем информацию о результате импорта
    return ImportResult(
        imported_slots=imported_slots,
        rooms_count=rooms_count,
        schedule_slots_count=schedule_slots_count,
    )
