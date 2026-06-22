from datetime import date

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from roomkeeper.db.models import Base, Booking, Room, ScheduleSlot


def make_session_factory():
    # создаем временную базу данных в памяти
    engine = create_engine("sqlite:///:memory:", future=True)
    # создаем все таблицы в тестовой базе
    Base.metadata.create_all(engine)

    # возвращаем фабрику сессий
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )


def test_create_room_schedule_slot_and_booking() -> None:
    # создаем тестовую базу данных
    session_factory = make_session_factory()

    # открываем транзакцию для записи данных
    with session_factory.begin() as session:
        room = Room(name="605")     # создаем аудиторию
        session.add(room)           # добавляем аудиторию в сессию
        session.flush()             # получаем идентификатор созданной записи

        # создаем запись официального расписания
        schedule_slot = ScheduleSlot(
            room_id=room.id,
            weekday="Понедельник",
            start_time="08:45",
            end_time="10:20",
            week_type="all",
            source="test.pdf",
            raw_text="Математический анализ 605",
        )

        # создаем пользовательское бронирование
        booking = Booking(
            room_id=room.id,
            user_telegram_id="123456",
            user_name="student",
            booking_date=date(2026, 6, 20),
            start_time="12:50",
            end_time="14:25",
            purpose="Встреча проектной команды",
            status="pending",
        )

        # добавляем созданные объекты в базу данных
        session.add(schedule_slot)
        session.add(booking)

    # открываем новую сессию для проверки данных
    with session_factory() as session:
        # ищем аудиторию 605
        room = session.scalar(select(Room).where(Room.name == "605"))

        assert room is not None                         # проверяем существование аудитории
        assert room.name == "605"                       # проверяем название аудитории
        assert len(room.schedule_slots) == 1            # проверяем количество записей расписания
        assert len(room.bookings) == 1                  # проверяем количество бронирований
        assert room.schedule_slots[0].weekday == "Понедельник"      # проверяем день недели занятия
        assert room.bookings[0].status == "pending"     # проверяем статус бронирования
