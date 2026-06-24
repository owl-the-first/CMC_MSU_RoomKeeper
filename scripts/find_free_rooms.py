from __future__ import annotations

import argparse
from datetime import date

from roomkeeper.db.session import DEFAULT_DATABASE_URL, get_session_factory
from roomkeeper.search.free_rooms import find_free_rooms, get_room_availability


def parse_args() -> argparse.Namespace:
    """Разбирает аргументы командной строки."""

    parser = argparse.ArgumentParser(
        description="Поиск свободных аудиторий по дате и времени."
    )

    parser.add_argument(
        "--date",
        required=True,
        help="Дата в формате YYYY-MM-DD, например 2026-06-22.",
    )

    parser.add_argument(
        "--start",
        required=True,
        help="Время начала в формате HH:MM, например 08:45.",
    )

    parser.add_argument(
        "--end",
        required=True,
        help="Время окончания в формате HH:MM, например 10:20.",
    )

    parser.add_argument(
        "--week-type",
        default="all",
        choices=["all", "even", "odd"],
        help="Тип недели: all, even или odd.",
    )

    parser.add_argument(
        "--room",
        default=None,
        help="Фильтр по названию аудитории, например 605 или П-13.",
    )

    parser.add_argument(
        "--show-busy",
        action="store_true",
        help="Показать не только свободные, но и занятые аудитории.",
    )

    parser.add_argument(
        "--database-url",
        default=DEFAULT_DATABASE_URL,
        help="Адрес базы данных SQLAlchemy.",
    )

    return parser.parse_args()


def main() -> None:
    """Запускает поиск свободных аудиторий."""

    args = parse_args()
    booking_date = date.fromisoformat(args.date)

    session_factory = get_session_factory(args.database_url)

    with session_factory() as session:
        if args.show_busy:
            rooms = get_room_availability(
                session=session,
                booking_date=booking_date,
                start_time=args.start,
                end_time=args.end,
                week_type=args.week_type,
                room_query=args.room,
            )
        else:
            rooms = find_free_rooms(
                session=session,
                booking_date=booking_date,
                start_time=args.start,
                end_time=args.end,
                week_type=args.week_type,
                room_query=args.room,
            )

    if not rooms:
        print("Аудитории не найдены.")
        return

    if args.show_busy:
        print("Состояние аудиторий:")

        for room in rooms:
            status = "свободна" if room.is_free else "занята"
            print(f"- {room.room_name}: {status}")

            for conflict in room.schedule_conflicts:
                print(f"  расписание: {conflict}")

            for conflict in room.booking_conflicts:
                print(f"  бронь: {conflict}")

        return

    print("Свободные аудитории:")

    for room in rooms:
        print(f"- {room.room_name}")


if __name__ == "__main__":
    main()
