"""Command line entry point for importing parsed schedule to the database."""

from pathlib import Path

from roomkeeper.db.import_schedule import import_schedule_slots
from roomkeeper.db.session import DEFAULT_DATABASE_URL

SCHEDULE_JSON = Path("data/parsed/schedule_slots.json")


def main() -> None:
    """Import parsed schedule slots from JSON to the database."""

    result = import_schedule_slots(SCHEDULE_JSON)

    print(f"Database: {DEFAULT_DATABASE_URL}")
    print(f"Imported slots: {result.imported_slots}")
    print(f"Rooms in DB: {result.rooms_count}")
    print(f"Schedule slots in DB: {result.schedule_slots_count}")