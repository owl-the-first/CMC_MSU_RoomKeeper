from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from roomkeeper.booking.bookings import (
    cancel_user_booking,
    get_room_names_for_bookings,
    get_user_bookings,
)
from roomkeeper.db.models import Base, Booking, Room


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


def add_booking(
    session,
    room_id: int,
    user_telegram_id: str,
    status: str = "pending",
) -> Booking:
    """Добавляет тестовую заявку."""

    booking = Booking(
        room_id=room_id,
        user_telegram_id=user_telegram_id,
        user_name="student",
        booking_date=date(2026, 6, 22),
        start_time="08:45",
        end_time="10:20",
        purpose="подготовка",
        status=status,
    )

    session.add(booking)
    session.flush()

    return booking


def test_get_user_bookings_returns_only_user_bookings() -> None:
    """Проверяем, что пользователь видит только свои заявки."""

    session_factory = make_session_factory()

    with session_factory.begin() as session:
        room = Room(name="605")
        session.add(room)
        session.flush()

        own_booking = add_booking(session, room.id, "123")
        own_booking_id = own_booking.id

        add_booking(session, room.id, "456")

    with session_factory() as session:
        bookings = get_user_bookings(session, "123")

    assert len(bookings) == 1
    assert bookings[0].id == own_booking_id


def test_get_room_names_for_bookings() -> None:
    """Проверяем получение названий аудиторий для заявок."""

    session_factory = make_session_factory()

    with session_factory.begin() as session:
        room = Room(name="605")
        session.add(room)
        session.flush()

        add_booking(session, room.id, "123")

    with session_factory() as session:
        bookings = get_user_bookings(session, "123")
        room_names = get_room_names_for_bookings(session, bookings)

    assert room_names == {bookings[0].room_id: "605"}


def test_cancel_user_booking_changes_status_to_canceled() -> None:
    """Проверяем успешную отмену своей заявки."""

    session_factory = make_session_factory()

    with session_factory.begin() as session:
        room = Room(name="605")
        session.add(room)
        session.flush()

        booking = add_booking(session, room.id, "123", status="pending")
        booking_id = booking.id

    with session_factory() as session:
        result = cancel_user_booking(session, booking_id, "123")

    with session_factory() as session:
        booking = session.get(Booking, booking_id)

    assert result.success
    assert booking is not None
    assert booking.status == "canceled"


def test_cancel_user_booking_rejects_other_user_booking() -> None:
    """Проверяем, что нельзя отменить чужую заявку."""

    session_factory = make_session_factory()

    with session_factory.begin() as session:
        room = Room(name="605")
        session.add(room)
        session.flush()

        booking = add_booking(session, room.id, "456", status="pending")
        booking_id = booking.id

    with session_factory() as session:
        result = cancel_user_booking(session, booking_id, "123")

    with session_factory() as session:
        booking = session.get(Booking, booking_id)

    assert not result.success
    assert "не найдена" in result.message
    assert booking is not None
    assert booking.status == "pending"


def test_cancel_user_booking_rejects_already_canceled_booking() -> None:
    """Проверяем повторную отмену уже отменённой заявки."""

    session_factory = make_session_factory()

    with session_factory.begin() as session:
        room = Room(name="605")
        session.add(room)
        session.flush()

        booking = add_booking(session, room.id, "123", status="canceled")
        booking_id = booking.id

    with session_factory() as session:
        result = cancel_user_booking(session, booking_id, "123")

    assert not result.success
    assert "уже отменена" in result.message


def test_cancel_user_booking_rejects_rejected_booking() -> None:
    """Проверяем отмену уже отклонённой заявки."""

    session_factory = make_session_factory()

    with session_factory.begin() as session:
        room = Room(name="605")
        session.add(room)
        session.flush()

        booking = add_booking(session, room.id, "123", status="rejected")
        booking_id = booking.id

    with session_factory() as session:
        result = cancel_user_booking(session, booking_id, "123")

    assert not result.success
    assert "уже отклонена" in result.message
