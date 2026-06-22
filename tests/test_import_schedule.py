import json

from roomkeeper.db.import_schedule import import_schedule_slots
from roomkeeper.db.repository import count_rooms, count_schedule_slots
from roomkeeper.db.session import get_session_factory


def test_import_schedule_slots_to_database(tmp_path) -> None:
    # пути к тестовому JSON-файлу и базе данных
    schedule_json = tmp_path / "schedule_slots.json"
    database_path = tmp_path / "test.db"

    # формируем адрес SQLite-базы данных
    database_url = f"sqlite:///{database_path}"

    # тестовые данные расписания
    data = [
        {
            "source_file": "test.pdf",
            "weekday": "Понедельник",
            "start_time": "08:45",
            "end_time": "10:20",
            "room": "605",
            "raw_line": "Математический анализ 605",
        },
        {
            "source_file": "test.pdf",
            "weekday": "Понедельник",
            "start_time": "10:30",
            "end_time": "12:05",
            "room": "605",
            "raw_line": "Практикум на ЭВМ 605",
        },
        {
            "source_file": "test.pdf",
            "weekday": "Вторник",
            "start_time": "12:50",
            "end_time": "14:25",
            "room": "П-13",
            "raw_line": "Алгебра П-13",
        },
    ]

    # сохраняем тестовые данные в JSON-файл
    schedule_json.write_text(
        json.dumps(data, ensure_ascii=False),
        encoding="utf-8",
    )

    # загружаем расписание в тестовую базу данных
    result = import_schedule_slots(
        json_path=schedule_json,
        database_url=database_url,
    )

    assert result.imported_slots == 3           # проверяем количество импортированных записей
    assert result.rooms_count == 2              # проверяем количество аудиторий
    assert result.schedule_slots_count == 3     # проверяем количество записей расписания

    # создаем фабрику сессий для работы с тестовой БД
    session_factory = get_session_factory(database_url)

    # открываем сессию и проверяем содержимое базы данных
    with session_factory() as session:
        assert count_rooms(session) == 2                # проверяем количество аудиторий
        assert count_schedule_slots(session) == 3       # проверяем количество записей расписания
