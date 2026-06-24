"""Command line entry point for showing database statistics."""

from sqlalchemy import select

from roomkeeper.db.models import Room, ScheduleSlot
from roomkeeper.db.repository import count_bookings, count_rooms, count_schedule_slots
from roomkeeper.db.session import DEFAULT_DATABASE_URL, get_session_factory


def main() -> None:
    """Print basic database statistics."""
    session_factory = get_session_factory(DEFAULT_DATABASE_URL)

    with session_factory() as session:
        rooms_count = count_rooms(session)
        schedule_slots_count = count_schedule_slots(session)
        bookings_count = count_bookings(session)

        print(f"Database: {DEFAULT_DATABASE_URL}")
        print(f"Rooms: {rooms_count}")
        print(f"Schedule slots: {schedule_slots_count}")
        print(f"Bookings: {bookings_count}")

        rooms = session.scalars(select(Room).order_by(Room.name).limit(10)).all()
        slots = session.scalars(select(ScheduleSlot).limit(5)).all()

        if rooms:
            print("First rooms:")
            for room in rooms:
                print(f"- {room.name}")

        if slots:
            print("First schedule slots:")
            for slot in slots:
                print(
                    f"- {slot.weekday} {slot.start_time}-{slot.end_time}: "
                    f"{slot.room.name}"
                )