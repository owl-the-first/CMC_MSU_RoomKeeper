from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from roomkeeper.db.models import Base, Booking, Room, ScheduleSlot
from roomkeeper.search.free_rooms import (
    find_free_rooms,
    get_room_availability,
    get_weekday_name,
    is_room_free,
    times_intersect,
)


def make_session_factory():
    """Создает временную SQLite-базу для тестов."""

    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )


def fill_test_data(session) -> None:
    """Заполняет тестовую базу аудиториями, расписанием и бронями."""

    room_605 = Room(name="605")
    room_731 = Room(name="731")
    room_p13 = Room(name="П-13")

    session.add_all([room_605, room_731, room_p13])
    session.flush()

    session.add(
        ScheduleSlot(
            room_id=room_605.id,
            weekday="Понедельник",
            start_time="08:45",
            end_time="10:20",
            week_type="all",
            subject="Математический анализ",
            raw_text="Математический анализ 605",
        )
    )

    session.add(
        ScheduleSlot(
            room_id=room_731.id,
            weekday="Понедельник",
            start_time="10:30",
            end_time="12:05",
            week_type="all",
            subject="Практикум на ЭВМ",
            raw_text="Практикум на ЭВМ 731",
        )
    )

    session.add(
        ScheduleSlot(
            room_id=room_p13.id,
            weekday="Понедельник",
            start_time="12:50",
            end_time="14:25",
            week_type="even",
            subject="Алгебра",
            raw_text="Алгебра П-13",
        )
    )

    session.add(
        Booking(
            room_id=room_605.id,
            user_telegram_id="123",
            user_name="student",
            booking_date=date(2026, 6, 22),
            start_time="12:50",
            end_time="14:25",
            purpose="Подготовка к защите проекта",
            status="pending",
        )
    )

    session.add(
        Booking(
            room_id=room_p13.id,
            user_telegram_id="456",
            user_name="other_student",
            booking_date=date(2026, 6, 22),
            start_time="08:45",
            end_time="10:20",
            purpose="Отклоненная заявка",
            status="rejected",
        )
    )


def test_get_weekday_name() -> None:
    """Проверяем перевод даты в день недели."""

    assert get_weekday_name(date(2026, 6, 22)) == "Понедельник"
    assert get_weekday_name(date(2026, 6, 23)) == "Вторник"


def test_times_intersect() -> None:
    """Проверяем пересечение временных интервалов."""

    assert times_intersect("08:45", "10:20", "09:00", "09:30")
    assert times_intersect("08:45", "10:20", "10:00", "10:30")
    assert not times_intersect("08:45", "10:20", "10:20", "10:30")
    assert not times_intersect("10:30", "12:05", "08:45", "10:20")


def test_find_free_rooms_uses_schedule_conflicts() -> None:
    """Аудитория с парой в расписании не должна считаться свободной."""

    session_factory = make_session_factory()

    with session_factory.begin() as session:
        fill_test_data(session)

    with session_factory() as session:
        free_rooms = find_free_rooms(
            session=session,
            booking_date=date(2026, 6, 22),
            start_time="08:45",
            end_time="10:20",
        )

    free_room_names = {room.room_name for room in free_rooms}

    assert "605" not in free_room_names
    assert "731" in free_room_names
    assert "П-13" in free_room_names


def test_find_free_rooms_uses_booking_conflicts() -> None:
    """Активная заявка на бронь должна занимать аудиторию."""

    session_factory = make_session_factory()

    with session_factory.begin() as session:
        fill_test_data(session)

    with session_factory() as session:
        free_rooms = find_free_rooms(
            session=session,
            booking_date=date(2026, 6, 22),
            start_time="12:50",
            end_time="14:25",
        )

    free_room_names = {room.room_name for room in free_rooms}

    assert "605" not in free_room_names
    assert "731" in free_room_names


def test_rejected_booking_does_not_block_room() -> None:
    """Отклоненная бронь не должна делать аудиторию занятой."""

    session_factory = make_session_factory()

    with session_factory.begin() as session:
        fill_test_data(session)

    with session_factory() as session:
        assert is_room_free(
            session=session,
            room_name="П-13",
            booking_date=date(2026, 6, 22),
            start_time="08:45",
            end_time="10:20",
        )


def test_week_type_is_used_for_schedule_slots() -> None:
    """Занятие по четной неделе блокирует аудиторию только для четной недели."""

    session_factory = make_session_factory()

    with session_factory.begin() as session:
        fill_test_data(session)

    with session_factory() as session:
        odd_week_rooms = find_free_rooms(
            session=session,
            booking_date=date(2026, 6, 22),
            start_time="12:50",
            end_time="14:25",
            week_type="odd",
        )

        even_week_rooms = find_free_rooms(
            session=session,
            booking_date=date(2026, 6, 22),
            start_time="12:50",
            end_time="14:25",
            week_type="even",
        )

    odd_week_room_names = {room.room_name for room in odd_week_rooms}
    even_week_room_names = {room.room_name for room in even_week_rooms}

    assert "П-13" in odd_week_room_names
    assert "П-13" not in even_week_room_names


def test_get_room_availability_shows_reasons() -> None:
    """Проверяем, что можно получить причину занятости аудитории."""

    session_factory = make_session_factory()

    with session_factory.begin() as session:
        fill_test_data(session)

    with session_factory() as session:
        availability = get_room_availability(
            session=session,
            booking_date=date(2026, 6, 22),
            start_time="08:45",
            end_time="10:20",
        )

    room_605 = next(room for room in availability if room.room_name == "605")

    assert not room_605.is_free
    assert room_605.schedule_conflicts
    assert "Математический анализ" in room_605.schedule_conflicts[0]
