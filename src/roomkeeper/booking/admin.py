from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from roomkeeper.db.models import Booking, Room
from roomkeeper.i18n import _


@dataclass(frozen=True)
class BookingReviewResult:
    """Результат одобрения или отклонения заявки администратором."""

    success: bool
    message: str
    booking_id: int | None = None
    user_telegram_id: str | None = None
    new_status: str | None = None


def get_booking_by_id(session: Session, booking_id: int) -> Booking | None:
    """Возвращает заявку по номеру."""
    return session.scalar(select(Booking).where(Booking.id == booking_id))


def get_pending_bookings(session: Session, limit: int = 20) -> list[Booking]:
    """Возвращает заявки, ожидающие решения администратора."""
    return list(
        session.scalars(
            select(Booking)
            .where(Booking.status == "pending")
            .order_by(Booking.id.asc())
            .limit(limit)
        )
    )


def get_room_name_for_booking(session: Session, booking: Booking) -> str:
    """Возвращает название аудитории для заявки."""
    room_name = session.scalar(select(Room.name).where(Room.id == booking.room_id))
    return room_name or f"id={booking.room_id}"


def approve_booking(session: Session, booking_id: int) -> BookingReviewResult:
    """Подтверждает заявку на бронирование."""
    booking = get_booking_by_id(session, booking_id)

    if booking is None:
        return BookingReviewResult(
            success=False,
            message=_("Заявка №{booking_id} не найдена.").format(booking_id=booking_id),
            booking_id=booking_id,
        )

    if booking.status == "approved":
        return BookingReviewResult(
            success=False,
            message=_("Заявка №{booking_id} уже подтверждена.").format(
                booking_id=booking_id
            ),
            booking_id=booking_id,
            user_telegram_id=booking.user_telegram_id,
            new_status=booking.status,
        )

    if booking.status != "pending":
        return BookingReviewResult(
            success=False,
            message=_(
                "Заявку №{booking_id} нельзя подтвердить, потому что её статус: {status}."
            ).format(booking_id=booking_id, status=booking.status),
            booking_id=booking_id,
            user_telegram_id=booking.user_telegram_id,
            new_status=booking.status,
        )

    booking.status = "approved"
    session.commit()

    return BookingReviewResult(
        success=True,
        message=_("Заявка №{booking_id} подтверждена.").format(booking_id=booking_id),
        booking_id=booking_id,
        user_telegram_id=booking.user_telegram_id,
        new_status="approved",
    )


def reject_booking(session: Session, booking_id: int) -> BookingReviewResult:
    """Отклоняет заявку на бронирование."""
    booking = get_booking_by_id(session, booking_id)

    if booking is None:
        return BookingReviewResult(
            success=False,
            message=_("Заявка №{booking_id} не найдена.").format(booking_id=booking_id),
            booking_id=booking_id,
        )

    if booking.status == "rejected":
        return BookingReviewResult(
            success=False,
            message=_("Заявка №{booking_id} уже отклонена.").format(
                booking_id=booking_id
            ),
            booking_id=booking_id,
            user_telegram_id=booking.user_telegram_id,
            new_status=booking.status,
        )

    if booking.status != "pending":
        return BookingReviewResult(
            success=False,
            message=_(
                "Заявку №{booking_id} нельзя отклонить, потому что её статус: {status}."
            ).format(booking_id=booking_id, status=booking.status),
            booking_id=booking_id,
            user_telegram_id=booking.user_telegram_id,
            new_status=booking.status,
        )

    booking.status = "rejected"
    session.commit()

    return BookingReviewResult(
        success=True,
        message=_("Заявка №{booking_id} отклонена.").format(booking_id=booking_id),
        booking_id=booking_id,
        user_telegram_id=booking.user_telegram_id,
        new_status="rejected",
    )
