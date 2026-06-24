from pathlib import Path

from roomkeeper.parser import pdf_text


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