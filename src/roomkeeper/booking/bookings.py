from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from roomkeeper.db.models import Booking, Room
from roomkeeper.search.free_rooms import is_room_free


@dataclass(frozen=True)
class BookingCreationResult:
    """Результат попытки создать заявку на бронирование."""

    success: bool
    message: str
    booking_id: int | None = None


def find_room_by_name(session: Session, room_name: str) -> Room | None:
    """Ищет аудиторию по точному названию."""

    normalized_room_name = room_name.strip()

    return session.scalar(
        select(Room).where(Room.name == normalized_room_name)
    )


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
