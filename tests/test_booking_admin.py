from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from roomkeeper.booking.admin import approve_booking, get_pending_bookings, reject_booking
from roomkeeper.booking.bookings import create_booking_request
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


def add_pending_booking(session, room_id: int, user_telegram_id: str = "123") -> Booking:
    """Добавляет тестовую заявку в статусе pending."""

    booking = Booking(
        room_id=room_id,
        user_telegram_id=user_telegram_id,
        user_name="student",
        booking_date=date(2026, 2, 20),
        start_time="12:50",
        end_time="14:25",
        purpose="встреча проектной команды",
        status="pending",
    )
    session.add(booking)
    session.flush()
    return booking


def test_get_pending_bookings_returns_only_pending() -> None:
    """Проверяем выборку заявок, ожидающих решения."""

    session_factory = make_session_factory()

    with session_factory.begin() as session:
        room = Room(name="605")
        session.add(room)
        session.flush()

        pending_booking = add_pending_booking(session, room.id)
        pending_id = pending_booking.id

        session.add(
            Booking(
                room_id=room.id,
                user_telegram_id="456",
                user_name="other",
                booking_date=date(2026, 2, 21),
                start_time="08:45",
                end_time="10:20",
                purpose="другое",
                status="approved",
            )
        )

    with session_factory() as session:
        bookings = get_pending_bookings(session)

    assert len(bookings) == 1
    assert bookings[0].id == pending_id
    assert bookings[0].status == "pending"


def test_approve_booking_changes_status_to_approved() -> None:
    """Проверяем подтверждение заявки администратором."""

    session_factory = make_session_factory()

    with session_factory.begin() as session:
        room = Room(name="605")
        session.add(room)
        session.flush()
        booking = add_pending_booking(session, room.id)
        booking_id = booking.id

    with session_factory() as session:
        result = approve_booking(session, booking_id)

    with session_factory() as session:
        booking = session.get(Booking, booking_id)

    assert result.success
    assert result.new_status == "approved"
    assert result.user_telegram_id == "123"
    assert booking is not None
    assert booking.status == "approved"


def test_reject_booking_changes_status_to_rejected() -> None:
    """Проверяем отклонение заявки администратором."""

    session_factory = make_session_factory()

    with session_factory.begin() as session:
        room = Room(name="605")
        session.add(room)
        session.flush()
        booking = add_pending_booking(session, room.id)
        booking_id = booking.id

    with session_factory() as session:
        result = reject_booking(session, booking_id)

    with session_factory() as session:
        booking = session.get(Booking, booking_id)

    assert result.success
    assert result.new_status == "rejected"
    assert booking is not None
    assert booking.status == "rejected"


def test_approve_booking_rejects_non_pending_status() -> None:
    """Проверяем, что нельзя подтвердить уже отклонённую заявку."""

    session_factory = make_session_factory()

    with session_factory.begin() as session:
        room = Room(name="605")
        session.add(room)
        session.flush()
        booking = add_pending_booking(session, room.id)
        booking.status = "rejected"
        booking_id = booking.id

    with session_factory() as session:
        result = approve_booking(session, booking_id)

    assert not result.success
    assert "нельзя подтвердить" in result.message


def test_rejected_booking_does_not_block_new_booking() -> None:
    """Проверяем, что после отклонения аудитория снова доступна."""

    session_factory = make_session_factory()

    with session_factory.begin() as session:
        session.add(Room(name="605"))

    with session_factory() as session:
        first_result = create_booking_request(
            session=session,
            room_name="605",
            user_telegram_id="123",
            user_name="student",
            booking_date=date(2026, 2, 20),
            start_time="12:50",
            end_time="14:25",
            purpose="первая заявка",
        )

    with session_factory() as session:
        reject_booking(session, first_result.booking_id)

    with session_factory() as session:
        second_result = create_booking_request(
            session=session,
            room_name="605",
            user_telegram_id="456",
            user_name="other",
            booking_date=date(2026, 2, 20),
            start_time="12:50",
            end_time="14:25",
            purpose="вторая заявка",
        )

    assert second_result.success


def test_approved_booking_blocks_room() -> None:
    """Проверяем, что подтверждённая заявка блокирует аудиторию."""

    session_factory = make_session_factory()

    with session_factory.begin() as session:
        session.add(Room(name="605"))

    with session_factory() as session:
        first_result = create_booking_request(
            session=session,
            room_name="605",
            user_telegram_id="123",
            user_name="student",
            booking_date=date(2026, 2, 20),
            start_time="12:50",
            end_time="14:25",
            purpose="первая заявка",
        )

    with session_factory() as session:
        approve_booking(session, first_result.booking_id)

    with session_factory() as session:
        second_result = create_booking_request(
            session=session,
            room_name="605",
            user_telegram_id="456",
            user_name="other",
            booking_date=date(2026, 2, 20),
            start_time="13:00",
            end_time="14:00",
            purpose="вторая заявка",
        )

    assert not second_result.success
    assert "занята" in second_result.message
