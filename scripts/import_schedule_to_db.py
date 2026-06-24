from pathlib import Path

from roomkeeper.db.import_schedule import import_schedule_slots
from roomkeeper.db.session import DEFAULT_DATABASE_URL

# путь к JSON-файлу с расписанием
SCHEDULE_JSON = Path("data/parsed/schedule_slots.json")


def main() -> None:
    # проверяем наличие файла с расписанием
    if not SCHEDULE_JSON.exists():
        print("No parsed schedule found.")
        print("Run first:")
        print("PYTHONPATH=src python scripts/update_schedule.py")
        return

    # загружаем расписание в базу данных
    result = import_schedule_slots(SCHEDULE_JSON)

    print(f"Database: {DEFAULT_DATABASE_URL}")                          # выводим адрес базы данных
    print(f"Imported slots: {result.imported_slots}")                   # выводим количество импортированных записей
    print(f"Rooms in DB: {result.rooms_count}")                         # выводим количество аудиторий
    print(f"Schedule slots in DB: {result.schedule_slots_count}")       # выводим количество записей расписания


if __name__ == "__main__":
    main()
