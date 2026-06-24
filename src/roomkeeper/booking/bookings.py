from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from roomkeeper.db.models import Booking, Room
from roomkeeper.search.free_rooms import is_room_free


ACTIVE_BOOKING_STATUSES = {"pending", "approved"}


@dataclass(frozen=True)
class BookingCreationResult:
    """Результат попытки создать заявку на бронирование."""

    success: bool
    message: str
    booking_id: int | None = None


@dataclass(frozen=True)
class BookingCancelResult:
    """Результат попытки отменить заявку на бронирование."""

    success: bool
    message: str
    booking_id: int | None = None


def find_room_by_name(session: Session, room_name: str) -> Room | None:
    """Ищет аудиторию по точному названию."""

    normalized_room_name = room_name.strip()

    return session.scalar(select(Room).where(Room.name == normalized_room_name))


def create_booking_request(
    session: Session,
    room_name: str,
    user_telegram_id: str,
    user_name: str | None,
    booking_date: date,
    start_time: str,
    end_time: str,
    purpose: str,
    week_type: str = "all",
) -> BookingCreationResult:
    """Создаёт заявку на бронирование аудитории, если аудитория свободна."""

    room = find_room_by_name(session, room_name)

    if room is None:
        return BookingCreationResult(
            success=False,
            message=f"Аудитория {room_name} не найдена в базе.",
        )

    if not purpose.strip():
        return BookingCreationResult(
            success=False,
            message="Нужно указать цель бронирования.",
        )

    room_is_free = is_room_free(
        session=session,
        room_name=room.name,
        booking_date=booking_date,
        start_time=start_time,
        end_time=end_time,
        week_type=week_type,
    )

    if not room_is_free:
        return BookingCreationResult(
            success=False,
            message=(
                f"Аудитория {room.name} занята "
                f"{booking_date.isoformat()} с {start_time} до {end_time}."
            ),
        )

    booking = Booking(
        room_id=room.id,
        user_telegram_id=user_telegram_id,
        user_name=user_name,
        booking_date=booking_date,
        start_time=start_time,
        end_time=end_time,
        purpose=purpose.strip(),
        status="pending",
    )

    session.add(booking)
    session.commit()
    session.refresh(booking)

    return BookingCreationResult(
        success=True,
        message=(
            "Заявка на бронирование создана.\n\n"
            f"Номер заявки: {booking.id}\n"
            f"Аудитория: {room.name}\n"
            f"Дата: {booking_date.isoformat()}\n"
            f"Время: {start_time}–{end_time}\n"
            f"Цель: {purpose.strip()}\n"
            "Статус: pending"
        ),
        booking_id=booking.id,
    )


def get_user_bookings(
    session: Session,
    user_telegram_id: str,
    limit: int = 10,
) -> list[Booking]:
    """Возвращает последние заявки пользователя."""

    return list(
        session.scalars(
            select(Booking)
            .where(Booking.user_telegram_id == user_telegram_id)
            .order_by(Booking.id.desc())
            .limit(limit)
        )
    )


def get_room_names_for_bookings(
    session: Session,
    bookings: list[Booking],
) -> dict[int, str]:
    """Возвращает названия аудиторий для списка заявок."""

    room_ids = {booking.room_id for booking in bookings}

    if not room_ids:
        return {}

    rows = session.execute(select(Room.id, Room.name).where(Room.id.in_(room_ids))).all()

    return {room_id: room_name for room_id, room_name in rows}


def cancel_user_booking(
    session: Session,
    booking_id: int,
    user_telegram_id: str,
) -> BookingCancelResult:
    """Отменяет заявку пользователя, если она принадлежит ему и ещё активна."""

    booking = session.scalar(
        select(Booking).where(
            Booking.id == booking_id,
            Booking.user_telegram_id == user_telegram_id,
        )
    )

    if booking is None:
        return BookingCancelResult(
            success=False,
            message=f"Заявка №{booking_id} не найдена среди ваших заявок.",
            booking_id=booking_id,
        )

    if booking.status == "canceled":
        return BookingCancelResult(
            success=False,
            message=f"Заявка №{booking_id} уже отменена.",
            booking_id=booking_id,
        )

    if booking.status == "rejected":
        return BookingCancelResult(
            success=False,
            message=f"Заявка №{booking_id} уже отклонена, отменять её не нужно.",
            booking_id=booking_id,
        )

    if booking.status not in ACTIVE_BOOKING_STATUSES:
        return BookingCancelResult(
            success=False,
            message=(
                f"Заявку №{booking_id} нельзя отменить, "
                f"потому что её статус: {booking.status}."
            ),
            booking_id=booking_id,
        )

    booking.status = "canceled"
    session.commit()

    return BookingCancelResult(
        success=True,
        message=f"Заявка №{booking_id} отменена.",
        booking_id=booking_id,
    )
