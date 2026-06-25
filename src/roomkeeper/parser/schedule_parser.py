import re

from roomkeeper.parser.models import OccupancySlot
from roomkeeper.parser.rooms import extract_rooms_from_line

# Список дней недели, встречающихся в расписании.
WEEKDAYS = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
]


# Регулярное выражение для поиска временного интервала:
# поддерживает форматы 8.45 - 10.20 и 8:45 - 10:20.
TIME_RE = re.compile(
    r"(\d{1,2})[.:](\d{2})\s*[-–]\s*(\d{1,2})[.:](\d{2})"
)


def _find_weekday(line: str) -> str | None:
    """Ищет день недели в строке расписания."""
    for weekday in WEEKDAYS:
        if weekday.lower() in line.lower():
            return weekday

    return None


def _remove_weekday(line: str, weekday: str) -> str:
    """Удаляет найденный день недели из строки, оставляя остальной текст."""
    return re.sub(re.escape(weekday), "", line, count=1, flags=re.IGNORECASE).strip()


def _format_time_interval(match: re.Match[str]) -> tuple[str, str]:
    """Преобразует найденный интервал времени к формату ЧЧ:ММ."""
    start_hour, start_minute, end_hour, end_minute = match.groups()

    start_time = f"{int(start_hour):02d}:{start_minute}"
    end_time = f"{int(end_hour):02d}:{end_minute}"

    return start_time, end_time


def _add_slots_from_text(
    slots: list[OccupancySlot],
    *,
    source_file: str,
    weekday: str | None,
    start_time: str | None,
    end_time: str | None,
    text: str,
    raw_line: str,
) -> None:
    """Добавляет занятость аудиторий из куска текста для текущей пары."""
    if weekday is None or start_time is None or end_time is None:
        return

    rooms = extract_rooms_from_line(text)

    for room in rooms:
        slots.append(
            OccupancySlot(
                source_file=source_file,
                weekday=weekday,
                start_time=start_time,
                end_time=end_time,
                room=room,
                raw_line=raw_line,
            )
        )


def parse_lines(lines: list[str], source_file: str) -> list[OccupancySlot]:
    """Парсит строки PDF и возвращает занятость аудиторий."""
    slots: list[OccupancySlot] = []

    current_weekday: str | None = None
    current_start_time: str | None = None
    current_end_time: str | None = None

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            continue

        # Если встретился новый день, сбрасываем текущую пару.
        weekday = _find_weekday(line)

        if weekday is not None:
            current_weekday = weekday
            current_start_time = None
            current_end_time = None
            line = _remove_weekday(line, weekday)

        time_matches = list(TIME_RE.finditer(line))

        if time_matches:
            # Обрабатываем строку слева направо:
            # текст после времени относится к нему до следующего времени.
            for index, match in enumerate(time_matches):
                start_time, end_time = _format_time_interval(match)

                text_start = match.end()
                if index + 1 < len(time_matches):
                    text_end = time_matches[index + 1].start()
                else:
                    text_end = len(line)

                text_after_time = line[text_start:text_end].strip(" ,;")

                _add_slots_from_text(
                    slots,
                    source_file=source_file,
                    weekday=current_weekday,
                    start_time=start_time,
                    end_time=end_time,
                    text=text_after_time,
                    raw_line=text_after_time,
                )

            # Следующие строки без времени относятся к последнему найденному времени.
            current_start_time, current_end_time = _format_time_interval(time_matches[-1])
            continue

        # Если в строке нет времени, она относится к последней встреченной паре.
        _add_slots_from_text(
            slots,
            source_file=source_file,
            weekday=current_weekday,
            start_time=current_start_time,
            end_time=current_end_time,
            text=line,
            raw_line=raw_line,
        )

    return slots