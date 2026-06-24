from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовый класс для всех таблиц проекта."""


# модель аудитории ВМК; содержит информацию об аудитории и связанных объектах
class Room(Base):
    """Аудитория ВМК."""

    # имя таблицы в базе данных
    __tablename__ = "rooms"

    # уникальный идентификатор аудитории
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # название аудитории (731, П-13 и тд)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    # здание, в котором расположена аудитория
    building: Mapped[str] = mapped_column(String(100), default="ВМК", nullable=False)

    # дополнительное описание аудитории
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)

    # связанные записи официального расписания
    schedule_slots: Mapped[list[ScheduleSlot]] = relationship(
        back_populates="room",
        cascade="all, delete-orphan",
    )

    # связанные пользовательские бронирования
    bookings: Mapped[list[Booking]] = relationship(
        back_populates="room",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Возвращает строковое представление аудитории."""
        # удобное строковое представление объекта
        return f"Room(id={self.id!r}, name={self.name!r})"


# модель записи официального расписания; хранит информацию о занятии в аудитории
class ScheduleSlot(Base):
    """Занятость аудитории из официального расписания."""

    # имя таблицы в базе данных
    __tablename__ = "schedule_slots"

    # уникальный идентификатор записи
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # ссылка на таблицу аудиторий
    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    # день недели проведения занятия
    weekday: Mapped[str] = mapped_column(String(20), nullable=False)
    # время начала занятия
    start_time: Mapped[str] = mapped_column(String(5), nullable=False)
    # время окончания занятия
    end_time: Mapped[str] = mapped_column(String(5), nullable=False)

    # тип недели (все недели, четная, нечетная)
    week_type: Mapped[str] = mapped_column(String(20), default="all", nullable=False)

    # номер группы
    group_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # название предмета
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # ФИО преподавателя
    teacher: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # файл, из которого была получена запись
    source: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    # исходная строка расписания
    raw_text: Mapped[str] = mapped_column(Text, default="", nullable=False)

    # связь с объектом аудитории
    room: Mapped[Room] = relationship(back_populates="schedule_slots")

    # индекс для ускорения поиска по дню и времени
    __table_args__ = (
        Index("ix_schedule_weekday_time", "weekday", "start_time", "end_time"),
    )

    def __repr__(self) -> str:
        """Возвращает строковое представление занятия из расписания."""
        # удобное строковое представление объекта
        return (
            f"ScheduleSlot(id={self.id!r}, room_id={self.room_id!r}, "
            f"weekday={self.weekday!r}, time={self.start_time!r}-{self.end_time!r})"
        )


# модель пользовательского бронирования; хранит информацию о заявках из Telegram-бота
class Booking(Base):
    """Бронирование аудитории пользователем Telegram-бота."""

    # имя таблицы в базе данных
    __tablename__ = "bookings"

    # уникальный идентификатор бронирования
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # ссылка на аудиторию
    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    # Telegram ID пользователя
    user_telegram_id: Mapped[str] = mapped_column(String(50), nullable=False)
    # имя пользователя Telegram
    user_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # дата брони
    booking_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    # время начала брони
    start_time: Mapped[str] = mapped_column(String(5), nullable=False)
    # время окончания брони
    end_time: Mapped[str] = mapped_column(String(5), nullable=False)

    # назначение бронирования
    purpose: Mapped[str] = mapped_column(Text, default="", nullable=False)
    # статус заявки
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True, nullable=False)

    # время создания записи
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    # связь с объектом аудитории
    room: Mapped[Room] = relationship(back_populates="bookings")

    # индекс для ускорения поиска по дате и времени
    __table_args__ = (
        Index("ix_booking_date_time", "booking_date", "start_time", "end_time"),
    )

    def __repr__(self) -> str:
        """Возвращает строковое представление заявки на бронирование."""
        # удобное строковое представление объекта
        return (
            f"Booking(id={self.id!r}, room_id={self.room_id!r}, "
            f"date={self.booking_date!r}, time={self.start_time!r}-{self.end_time!r})"
        )
