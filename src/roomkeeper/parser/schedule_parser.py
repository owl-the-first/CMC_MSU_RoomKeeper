import re

from roomkeeper.parser.models import OccupancySlot
from roomkeeper.parser.rooms import extract_rooms_from_line

# список дней недели, встречающихся в расписании
WEEKDAYS = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
]

# регулярное выражение для поиска временного интервала; поддерживает форматы 8.45 - 10.20 и 8:45 - 10:20
TIME_RE = re.compile(
    r"(\d{1,2})[.:](\d{2})\s*[-–]\s*(\d{1,2})[.:](\d{2})"
)


def _find_weekday(line: str) -> str | None:
    # проверяем, содержит ли строка день недели
    for weekday in WEEKDAYS:
        if weekday.lower() in line.lower():
            return weekday

    # если день недели не найден -> возвращаем None
    return None


def _find_time_interval(line: str) -> tuple[str, str] | None:
    # ищем в строке промежуток времени
    match = TIME_RE.search(line)

    # если время не найдено -> возвращаем None
    if not match:
        return None

    # извлекаем часы и минуты начала и конца пары
    start_hour, start_minute, end_hour, end_minute = match.groups()

    # приводим время к формату ЧЧ:ММ
    start_time = f"{int(start_hour):02d}:{start_minute}"
    end_time = f"{int(end_hour):02d}:{end_minute}"

    # возвращаем начало и конец пары
    return start_time, end_time


def _is_empty_first_pair_for_320_group(
    source_file: str,
    weekday: str | None,
    group_header: str | None,
    start_time: str,
    end_time: str,
) -> bool:
    """Проверяет известный случай: у групп 320-328 в понедельник первая пара пустая."""
    required_groups = ["320", "321", "323", "324", "325", "327", "328"]

    if not source_file.endswith("3_kurs_vesna_2026_14.pdf"):
        return False

    if weekday != "Понедельник":
        return False

    if group_header is None:
        return False

    if start_time != "08:45" or end_time != "10:20":
        return False

    groups_in_header = group_header.split()

    return all(group in groups_in_header for group in required_groups)


def parse_lines(lines: list[str], source_file: str) -> list[OccupancySlot]:
    """Парсит строки PDF и возвращает занятость аудиторий."""
    # список найденных записей о занятости
    slots: list[OccupancySlot] = []

    current_weekday: str | None = None
    current_start_time: str | None = None
    current_end_time: str | None = None

    # последовательно обрабатываем все строки
    for line in lines:

        # проверяем, не встретился ли новый день недели
        weekday = _find_weekday(line)
        if weekday is not None:
            current_weekday = weekday
            current_start_time = None
            current_end_time = None
            continue

        # проверяем, не содержит ли строка время пары
        time_interval = _find_time_interval(line)
        if time_interval is not None:
            current_start_time, current_end_time = time_interval

        # ищем аудитории в текущей строке
        line_without_time = TIME_RE.sub("", line).strip()

        if line_without_time and line_without_time in extract_rooms_from_line(line_without_time):
            continue

        rooms = extract_rooms_from_line(line_without_time)

        # если аудиторий нет -> переходим к следующей строке
        if not rooms:
            continue

        # если неизвестен день или время, то запись создать нельзя
        if current_weekday is None or current_start_time is None or current_end_time is None:
            continue

        # создаем запись для каждой найденной аудитории
        for room in rooms:
            slots.append(
                OccupancySlot(
                    source_file=source_file,
                    weekday=current_weekday,
                    start_time=current_start_time,
                    end_time=current_end_time,
                    room=room,
                    raw_line=line,
                )
            )

    # возвращаем список найденных занятий
    return slots
