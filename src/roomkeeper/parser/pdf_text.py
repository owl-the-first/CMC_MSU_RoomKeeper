import re
from pathlib import Path

import pdfplumber

WEEKDAYS = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
]


TIME_RE = re.compile(
    r"(\d{1,2})[.:](\d{2})\s*[-–]\s*(\d{1,2})[.:](\d{2})"
)


GROUP_RE = re.compile(r"\d{3}(?:[-–]?[а-яА-Я])?")


TABLE_SETTINGS = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    "snap_tolerance": 3,
    "join_tolerance": 3,
    "intersection_tolerance": 5,
}


def _normalize_cell(cell: object) -> str:
    """Приводит ячейку таблицы к одной строке без лишних пробелов."""
    if cell is None:
        return ""

    text = str(cell)
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def _find_weekday(text: str) -> str | None:
    """Ищет день недели в тексте строки таблицы."""
    lowered_text = text.lower()

    for weekday in WEEKDAYS:
        if weekday.lower() in lowered_text:
            return weekday

    return None


def _format_time_interval(match: re.Match[str]) -> tuple[str, str]:
    """Преобразует найденный интервал времени к формату HH:MM."""
    start_hour, start_minute, end_hour, end_minute = match.groups()

    start_time = f"{int(start_hour):02d}:{start_minute}"
    end_time = f"{int(end_hour):02d}:{end_minute}"

    return start_time, end_time


def _looks_like_lesson_cell(cell: str) -> bool:
    """Проверяет, что ячейка похожа на занятие, а не только на время/аудиторию."""
    text = TIME_RE.sub(" ", cell)
    text = re.sub(r"П\s*[-–]?\s*\d{1,2}[а-яА-Я]?", " ", text)
    text = re.sub(r"МЗ\s*[-–]\s*\d{1,2}", " ", text)
    text = re.sub(
        r"(?<!\d)[1-9]\d{1,2}(?:\s*[-–]\s*[а-яА-Я]|[а-яА-Я])?(?!\d)",
        " ",
        text,
    )

    return re.search(r"[А-Яа-яЁё]", text) is not None


def _is_group_header_row(cells: list[str]) -> bool:
    """Проверяет, что строка таблицы является строкой с номерами групп."""
    content_cells = [cell for cell in cells[1:] if cell]

    if len(content_cells) < 2:
        return False

    group_cells_count = sum(
        1 for cell in content_cells if GROUP_RE.fullmatch(cell)
    )

    return group_cells_count >= len(content_cells) * 0.7


def _lines_from_table(table: list[list[object]]) -> list[str]:
    """Преобразует таблицу PDF в логические строки расписания."""
    lines: list[str] = []

    current_weekday: str | None = None
    current_start_time: str | None = None
    current_end_time: str | None = None

    for row in table:
        cells = [_normalize_cell(cell) for cell in row]

        if not cells:
            continue

        row_text = " ".join(cell for cell in cells if cell)

        if not row_text:
            continue

        weekday = _find_weekday(row_text)

        if weekday is not None:
            current_weekday = weekday

        if _is_group_header_row(cells):
            current_start_time = None
            current_end_time = None
            continue

        first_cell = cells[0]
        time_match = TIME_RE.search(first_cell)

        if time_match is not None:
            current_start_time, current_end_time = _format_time_interval(time_match)

        if (
            current_weekday is None
            or current_start_time is None
            or current_end_time is None
        ):
            continue

        content_cells = cells[1:]

        for content in content_cells:
            if not content:
                continue

            if not _looks_like_lesson_cell(content):
                continue

            lines.append(
                f"{current_weekday} {current_start_time} - {current_end_time} {content}"
            )

    return lines


def _plain_text_lines(page: pdfplumber.page.Page) -> list[str]:
    """Извлекает обычные строки текста со страницы, если таблица не нашлась."""
    text = page.extract_text() or ""

    return [line.strip() for line in text.splitlines() if line.strip()]


def extract_lines_from_pdf(pdf_path: Path) -> list[str]:
    """Извлекает строки расписания из PDF-файла."""
    lines: list[str] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_lines: list[str] = []

            extract_tables = getattr(page, "extract_tables", None)

            if extract_tables is not None:
                tables = extract_tables(table_settings=TABLE_SETTINGS)

                for table in tables:
                    page_lines.extend(_lines_from_table(table))

            if page_lines:
                lines.extend(page_lines)
            else:
                lines.extend(_plain_text_lines(page))

    return lines