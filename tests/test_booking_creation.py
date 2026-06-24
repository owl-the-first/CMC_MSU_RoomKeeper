from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from roomkeeper.booking.bookings import create_booking_request
from roomkeeper.db.models import Base, Booking, Room, ScheduleSlot


def make_session_factory():
    """Создаёт временную SQLite-базу для тестов."""

    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )


def test_create_booking_request_creates_pending_booking() -> None:
    """Проверяем создание заявки на свободную аудиторию."""

    session_factory = make_session_factory()

    with session_factory.begin() as session:
        session.add(Room(name="605"))

    with session_factory() as session:
        result = create_booking_request(
            session=session,
            room_name="605",
            user_telegram_id="123",
            user_name="student",
            booking_date=date(2026, 6, 22),
            start_time="08:45",
            end_time="10:20",
            purpose="подготовка к защите",
        )

    with session_factory() as session:
        bookings = list(session.query(Booking).all())

    assert result.success
    assert result.booking_id is not None
    assert len(bookings) == 1
    assert bookings[0].status == "pending"
    assert bookings[0].purpose == "подготовка к защите"


def test_create_booking_request_rejects_unknown_room() -> None:
    """Проверяем, что нельзя забронировать несуществующую аудиторию."""

    session_factory = make_session_factory()

    with session_factory() as session:
        result = create_booking_request(
            session=session,
            room_name="999",
            user_telegram_id="123",
            user_name="student",
            booking_date=date(2026, 6, 22),
            start_time="08:45",
            end_time="10:20",
            purpose="подготовка",
        )

    assert not result.success
    assert "не найдена" in result.message


def test_create_booking_request_rejects_busy_room_by_schedule() -> None:
    """Проверяем, что нельзя создать бронь поверх официального расписания."""

    session_factory = make_session_factory()

    with session_factory.begin() as session:
        room = Room(name="605")
        session.add(room)
        session.flush()

        session.add(
            ScheduleSlot(
                room_id=room.id,
                weekday="Понедельник",
                start_time="08:45",
                end_time="10:20",
                week_type="all",
                subject="Математический анализ",
                raw_text="Математический анализ 605",
            )
        )

    with session_factory() as session:
        result = create_booking_request(
            session=session,
            room_name="605",
            user_telegram_id="123",
            user_name="student",
            booking_date=date(2026, 6, 22),
            start_time="08:45",
            end_time="10:20",
            purpose="подготовка",
        )

    assert not result.success
    assert "занята" in result.message


def test_create_booking_request_rejects_busy_room_by_booking() -> None:
    """Проверяем, что нельзя создать две активные брони на одно время."""

    session_factory = make_session_factory()

    with session_factory.begin() as session:
        room = Room(name="605")
        session.add(room)
        session.flush()

        session.add(
            Booking(
                room_id=room.id,
                user_telegram_id="456",
                user_name="other_student",
                booking_date=date(2026, 6, 22),
                start_time="08:45",
                end_time="10:20",
                purpose="другая встреча",
                status="pending",
            )
        )

    with session_factory() as session:
        result = create_booking_request(
            session=session,
            room_name="605",
            user_telegram_id="123",
            user_name="student",
            booking_date=date(2026, 6, 22),
            start_time="09:00",
            end_time="09:30",
            purpose="подготовка",
        )

    assert not result.success
    assert "занята" in result.message
