from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from roomkeeper.db.models import Booking, Room, ScheduleSlot


def get_or_create_room(
    session: Session,
    room_name: str,
    building: str = "ВМК",
    description: str = "",
) -> Room:
    """Возвращает аудиторию из БД или создает новую."""
    # удаляем лишние пробелы в названии аудитории
    room_name = room_name.strip()

    # ищем аудиторию в базе данных
    room = session.scalar(select(Room).where(Room.name == room_name))

    # если аудитория уже существует, возвращаем ее
    if room is not None:
        return room

    # создаем новую аудиторию
    room = Room(
        name=room_name,
        building=building,
        description=description,
    )
    session.add(room)       # добавляем объект в текущую сессию
    session.flush()         # отправляем изменения в БД без фиксации транзакции

    return room             # возвращаем созданную аудиторию


def add_schedule_slot(
    session: Session,
    room_name: str,
    weekday: str,
    start_time: str,
    end_time: str,
    week_type: str = "all",
    group_name: str | None = None,
    subject: str | None = None,
    teacher: str | None = None,
    source: str = "",
    raw_text: str = "",
) -> ScheduleSlot:
    """Добавляет запись о занятости аудитории из расписания."""
    # получаем аудиторию или создаем ее при необходимости
    room = get_or_create_room(session, room_name)

    # создаем новую запись расписания
    slot = ScheduleSlot(
        room_id=room.id,
        weekday=weekday,
        start_time=start_time,
        end_time=end_time,
        week_type=week_type,
        group_name=group_name,
        subject=subject,
        teacher=teacher,
        source=source,
        raw_text=raw_text,
    )

    session.add(slot)       # добавляем запись в сессию
    session.flush()         # отправляем изменения в БД без commit()

    return slot             # возвращаем созданную запись


def clear_schedule_slots(session: Session) -> None:
    """Удаляет старые записи официального расписания."""
    session.execute(delete(ScheduleSlot))


def count_rooms(session: Session) -> int:
    """Считает количество аудиторий."""
    return session.scalar(select(func.count()).select_from(Room)) or 0


def count_schedule_slots(session: Session) -> int:
    """Считает количество записей расписания."""
    return session.scalar(select(func.count()).select_from(ScheduleSlot)) or 0


def count_bookings(session: Session) -> int:
    """Считает количество бронирований."""
    return session.scalar(select(func.count()).select_from(Booking)) or 0


def delete_unused_rooms(session: Session) -> int:
    """Удаляет аудитории, у которых нет расписания и бронирований."""
    deleted_count = 0
    rooms = session.scalars(select(Room)).all()

    for room in rooms:
        has_schedule_slot = (
            session.scalar(
                select(ScheduleSlot.id)
                .where(ScheduleSlot.room_id == room.id)
                .limit(1)
            )
            is not None
        )

        has_booking = (
            session.scalar(
                select(Booking.id)
                .where(Booking.room_id == room.id)
                .limit(1)
            )
            is not None
        )

        if not has_schedule_slot and not has_booking:
            session.delete(room)
            deleted_count += 1

    return deleted_count