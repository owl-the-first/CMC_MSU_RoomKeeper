from sqlalchemy import select

from roomkeeper.db.models import Room, ScheduleSlot
from roomkeeper.db.repository import count_bookings, count_rooms, count_schedule_slots
from roomkeeper.db.session import DEFAULT_DATABASE_URL, get_session_factory


def main() -> None:
    """Показывает краткую статистику базы данных."""
    # создаем фабрику сессий для работы с базой данных
    session_factory = get_session_factory()

    # открываем сессию для чтения данных
    with session_factory() as session:
        # получаем количество аудиторий, занятий и бронирований
        rooms_count = count_rooms(session)
        schedule_slots_count = count_schedule_slots(session)        
        bookings_count = count_bookings(session)

        # выводим основную статистику базы данных
        print(f"Database: {DEFAULT_DATABASE_URL}")
        print(f"Rooms: {rooms_count}")
        print(f"Schedule slots: {schedule_slots_count}")
        print(f"Bookings: {bookings_count}")

        print()
        print("First rooms:")

        # получаем первые 20 аудиторий в алфавитном порядке
        rooms = session.scalars(
            select(Room).order_by(Room.name).limit(20)
        ).all()

        # выводим названия найденных аудиторий
        for room in rooms:
            print(f"- {room.name}")

        print()
        print("First schedule slots:")

        # получаем несколько первых записей расписания
        slots = session.scalars(
            select(ScheduleSlot)
            .join(Room)
            .order_by(ScheduleSlot.weekday, ScheduleSlot.start_time)
            .limit(10)
        ).all()

        # выводим информацию о занятиях
        for slot in slots:
            print(
                f"- {slot.weekday} "
                f"{slot.start_time}-{slot.end_time} "
                f"{slot.room.name} "
                f"source={slot.source}"
            )


if __name__ == "__main__":
    main()
