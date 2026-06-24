from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from roomkeeper.db.models import Booking, Room, ScheduleSlot

# Брони с такими статусами считаем занятыми.
# pending тоже блокирует аудиторию, чтобы две заявки не попали на одно время.
ACTIVE_BOOKING_STATUSES = ("pending", "approved")

# Названия дней недели в том же виде, в котором они лежат в расписании.
WEEKDAY_NAMES = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
    "Воскресенье",
]


@dataclass(frozen=True)
class RoomAvailability:
    """Результат проверки одной аудитории на свободность."""

    room_id: int
    room_name: str
    is_free: bool
    schedule_conflicts: tuple[str, ...] = ()
    booking_conflicts: tuple[str, ...] = ()


def get_weekday_name(day: date) -> str:
    """Возвращает русское название дня недели для даты."""
    return WEEKDAY_NAMES[day.weekday()]


def time_to_minutes(value: str) -> int:
    """Переводит время HH:MM или HH.MM в количество минут от начала дня."""
    normalized = value.strip().replace(".", ":")
    parts = normalized.split(":")

    if len(parts) != 2:
        raise ValueError(f"Некорректное время: {value!r}")

    try:
        hours = int(parts[0])
        minutes = int(parts[1])
    except ValueError as error:
        raise ValueError(f"Некорректное время: {value!r}") from error

    if not 0 <= hours <= 23 or not 0 <= minutes <= 59:
        raise ValueError(f"Некорректное время: {value!r}")

    return hours * 60 + minutes


def times_intersect(
    first_start: str,
    first_end: str,
    second_start: str,
    second_end: str,
) -> bool:
    """Проверяет, пересекаются ли два временных интервала."""
    first_start_minutes = time_to_minutes(first_start)
    first_end_minutes = time_to_minutes(first_end)
    second_start_minutes = time_to_minutes(second_start)
    second_end_minutes = time_to_minutes(second_end)

    if first_start_minutes >= first_end_minutes:
        raise ValueError(f"Некорректный первый интервал: {first_start}-{first_end}")

    if second_start_minutes >= second_end_minutes:
        raise ValueError(f"Некорректный второй интервал: {second_start}-{second_end}")

    return first_start_minutes < second_end_minutes and second_start_minutes < first_end_minutes


def normalize_week_type(week_type: str) -> str:
    """Приводит тип недели к одному из вариантов: all, even, odd."""
    aliases = {
        "": "all",
        "all": "all",
        "все": "all",
        "каждая": "all",
        "четная": "even",
        "чётная": "even",
        "even": "even",
        "нечетная": "odd",
        "нечётная": "odd",
        "odd": "odd",
    }

    key = week_type.strip().lower()
    return aliases.get(key, key)


def slot_affects_week(slot_week_type: str, requested_week_type: str) -> bool:
    """Проверяет, относится ли запись расписания к нужному типу недели."""
    slot_week_type = normalize_week_type(slot_week_type)
    requested_week_type = normalize_week_type(requested_week_type)

    if requested_week_type == "all":
        return True

    return slot_week_type in ("all", requested_week_type)


def format_schedule_conflict(slot: ScheduleSlot) -> str:
    """Готовит понятное описание конфликта с официальным расписанием."""
    title = slot.subject or slot.raw_text or "занято по расписанию"
    return f"{slot.start_time}-{slot.end_time}: {title}"


def format_booking_conflict(booking: Booking) -> str:
    """Готовит понятное описание конфликта с пользовательской бронью."""
    purpose = booking.purpose or "бронь пользователя"
    user_name = booking.user_name or booking.user_telegram_id
    return f"{booking.start_time}-{booking.end_time}: {purpose} ({user_name})"


def get_room_availability(
    session: Session,
    booking_date: date,
    start_time: str,
    end_time: str,
    week_type: str = "all",
    room_query: str | None = None,
    active_booking_statuses: tuple[str, ...] = ACTIVE_BOOKING_STATUSES,
) -> list[RoomAvailability]:
    """Возвращает список аудиторий с информацией, свободны они или заняты."""
    if time_to_minutes(start_time) >= time_to_minutes(end_time):
        raise ValueError(f"Некорректный интервал поиска: {start_time}-{end_time}")

    weekday = get_weekday_name(booking_date)

    rooms = list(session.scalars(select(Room).order_by(Room.name)))

    if room_query is not None:
        query = room_query.strip().lower()
        rooms = [room for room in rooms if query in room.name.lower()]

    if not rooms:
        return []

    room_ids = {room.id for room in rooms}

    schedule_slots = list(
        session.scalars(
            select(ScheduleSlot).where(
                ScheduleSlot.weekday == weekday,
                ScheduleSlot.room_id.in_(room_ids),
            )
        )
    )

    bookings = list(
        session.scalars(
            select(Booking).where(
                Booking.booking_date == booking_date,
                Booking.room_id.in_(room_ids),
                Booking.status.in_(active_booking_statuses),
            )
        )
    )

    schedule_conflicts_by_room: dict[int, list[str]] = {}
    booking_conflicts_by_room: dict[int, list[str]] = {}

    for slot in schedule_slots:
        if not slot_affects_week(slot.week_type, week_type):
            continue

        if times_intersect(start_time, end_time, slot.start_time, slot.end_time):
            schedule_conflicts_by_room.setdefault(slot.room_id, []).append(
                format_schedule_conflict(slot)
            )

    for booking in bookings:
        if times_intersect(start_time, end_time, booking.start_time, booking.end_time):
            booking_conflicts_by_room.setdefault(booking.room_id, []).append(
                format_booking_conflict(booking)
            )

    result = []

    for room in rooms:
        schedule_conflicts = tuple(schedule_conflicts_by_room.get(room.id, []))
        booking_conflicts = tuple(booking_conflicts_by_room.get(room.id, []))

        result.append(
            RoomAvailability(
                room_id=room.id,
                room_name=room.name,
                is_free=not schedule_conflicts and not booking_conflicts,
                schedule_conflicts=schedule_conflicts,
                booking_conflicts=booking_conflicts,
            )
        )

    return result


def find_free_rooms(
    session: Session,
    booking_date: date,
    start_time: str,
    end_time: str,
    week_type: str = "all",
    room_query: str | None = None,
) -> list[RoomAvailability]:
    """Возвращает только свободные аудитории."""
    availability = get_room_availability(
        session=session,
        booking_date=booking_date,
        start_time=start_time,
        end_time=end_time,
        week_type=week_type,
        room_query=room_query,
    )

    return [room for room in availability if room.is_free]


def is_room_free(
    session: Session,
    room_name: str,
    booking_date: date,
    start_time: str,
    end_time: str,
    week_type: str = "all",
) -> bool:
    """Проверяет, свободна ли конкретная аудитория."""
    room_name = room_name.strip()

    availability = get_room_availability(
        session=session,
        booking_date=booking_date,
        start_time=start_time,
        end_time=end_time,
        week_type=week_type,
        room_query=room_name,
    )

    for room in availability:
        if room.room_name == room_name:
            return room.is_free

    return False
