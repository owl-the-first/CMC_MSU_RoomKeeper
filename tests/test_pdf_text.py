from pathlib import Path

from roomkeeper.parser import pdf_text
from roomkeeper.parser.pdf_text import _lines_from_table
from roomkeeper.parser.schedule_parser import parse_lines


def test_lines_from_table_does_not_shift_second_pair_to_empty_first_pair() -> None:
    table = [
        ["Понедельник", "320", "321", "323", "324", "325", "327", "328"],
        ["8.45-10.20", "", "", "", "", "", "", ""],
        [
            "10.30-12.05",
            "Формальные языки и автоматы Батузов К.А. П-8а",
            "",
            "Кулагин И.И. 523",
            "",
            "Беляев М.В. 510",
            "",
            "Кулагин И.И. Ледовских И.Н. 579",
        ],
    ]

    lines = _lines_from_table(table)
    slots = parse_lines(lines, source_file="test.pdf")

    p8a_slots = [slot for slot in slots if slot.room == "П-8а"]

    assert len(p8a_slots) == 1
    assert p8a_slots[0].weekday == "Понедельник"
    assert p8a_slots[0].start_time == "10:30"
    assert p8a_slots[0].end_time == "12:05"


class FakePage:
    """Тестовая страница PDF."""

    def __init__(self, text: str | None) -> None:
        self.text = text

    def extract_text(self) -> str | None:
        """Возвращает текст страницы."""

        return self.text


class FakePdf:
    """Тестовый PDF-файл для контекстного менеджера."""

    def __init__(self) -> None:
        self.pages = [
            FakePage(" первая строка \n\n вторая строка "),
            FakePage(None),
            FakePage(" третья строка "),
        ]

    def __enter__(self) -> "FakePdf":
        """Возвращает открытый PDF."""

        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Закрывает тестовый PDF."""

        return None


def test_extract_lines_from_pdf_returns_non_empty_stripped_lines(monkeypatch) -> None:
    """Проверяем извлечение непустых строк из PDF."""

    def fake_open(path: Path) -> FakePdf:
        assert path == Path("schedule.pdf")
        return FakePdf()

    monkeypatch.setattr(pdf_text.pdfplumber, "open", fake_open)

    lines = pdf_text.extract_lines_from_pdf(Path("schedule.pdf"))

    assert lines == [
        "первая строка",
        "вторая строка",
        "третья строка",
    ]


def test_lines_from_table_skips_group_header_rows() -> None:
    table = [
        ["Понедельник", "101-м", "102", "103-в", "104-в"],
        ["8.45-10.20", "", "", "", ""],
        ["10.30-12.05", "Формальные языки Батузов К.А. П-8а", "", "", ""],
    ]

    lines = _lines_from_table(table)

    assert lines == [
        "Понедельник 10:30 - 12:05 Формальные языки Батузов К.А. П-8а"
    ]


def test_lines_from_table_creates_separate_lines_for_cells() -> None:
    table = [
        ["Понедельник", "320", "321"],
        ["8.45-10.20", "Есикова Н.Б. 504", "Шишкин А.Г. 616"],
    ]

    lines = _lines_from_table(table)

    assert lines == [
        "Понедельник 08:45 - 10:20 Есикова Н.Б. 504",
        "Понедельник 08:45 - 10:20 Шишкин А.Г. 616",
    ]


def test_lines_from_table_skips_time_only_room_cells() -> None:
    table = [
        ["Понедельник", "320", "321"],
        ["8.45-10.20", "08:45 - 10:20 658", "Семёнов А.С. 658"],
    ]

    lines = _lines_from_table(table)

    assert lines == [
        "Понедельник 08:45 - 10:20 Семёнов А.С. 658",
    ]