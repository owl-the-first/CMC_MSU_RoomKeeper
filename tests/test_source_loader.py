from pathlib import Path

from roomkeeper.parser import source_loader
from roomkeeper.parser.models import SchedulePdf


class FakeResponse:
    """Тестовая замена HTTP-ответа requests."""

    def __init__(self, text: str = "", content: bytes = b"") -> None:
        self.text = text
        self.content = content
        self.status_checked = False

    def raise_for_status(self) -> None:
        """Запоминает, что код ответа был проверен."""

        self.status_checked = True


def test_fetch_html_downloads_page(monkeypatch) -> None:
    """Проверяем, что HTML-страница скачивается через requests."""

    calls = {}

    def fake_get(url: str, timeout: int) -> FakeResponse:
        calls["url"] = url
        calls["timeout"] = timeout
        return FakeResponse(text="<html>ok</html>")

    monkeypatch.setattr(source_loader.requests, "get", fake_get)

    html = source_loader.fetch_html("https://example.com/schedule")

    assert html == "<html>ok</html>"
    assert calls == {
        "url": "https://example.com/schedule",
        "timeout": 20,
    }


def test_find_schedule_pdfs_filters_schedule_links(monkeypatch) -> None:
    """Проверяем, что выбираются только PDF-файлы с расписанием."""

    html = """
    <html>
        <body>
            <a href="/files/1_kurs.pdf">1 курс</a>
            <a href="/files/chetnost.pdf">Четность недель</a>
            <a href="/files/info.txt">Обычный текстовый файл</a>
            <a href="/files/master.pdf">Магистратура</a>
            <a href="">Пустая ссылка</a>
        </body>
    </html>
    """

    monkeypatch.setattr(source_loader, "fetch_html", lambda url: html)

    pdfs = source_loader.find_schedule_pdfs("https://cs.msu.ru/studies/schedule")

    assert pdfs == [
        SchedulePdf(
            title="1 курс",
            url="https://cs.msu.ru/files/1_kurs.pdf",
            filename="1_kurs.pdf",
        ),
        SchedulePdf(
            title="Магистратура",
            url="https://cs.msu.ru/files/master.pdf",
            filename="master.pdf",
        ),
    ]


def test_download_pdf_skips_existing_file(monkeypatch, tmp_path: Path) -> None:
    """Проверяем, что уже скачанный PDF не скачивается повторно."""

    pdf = SchedulePdf(
        title="1 курс",
        url="https://cs.msu.ru/files/1_kurs.pdf",
        filename="1_kurs.pdf",
    )
    existing_file = tmp_path / "1_kurs.pdf"
    existing_file.write_bytes(b"old content")

    def fake_get(url: str, timeout: int) -> FakeResponse:
        raise AssertionError("requests.get не должен вызываться для готового файла")

    monkeypatch.setattr(source_loader.requests, "get", fake_get)

    result = source_loader.download_pdf(pdf, tmp_path)

    assert result == existing_file
    assert existing_file.read_bytes() == b"old content"


def test_download_pdf_downloads_missing_file(monkeypatch, tmp_path: Path) -> None:
    """Проверяем скачивание PDF, если файла ещё нет."""

    calls = {}
    pdf = SchedulePdf(
        title="1 курс",
        url="https://cs.msu.ru/files/1_kurs.pdf",
        filename="1_kurs.pdf",
    )

    def fake_get(url: str, timeout: int) -> FakeResponse:
        calls["url"] = url
        calls["timeout"] = timeout
        return FakeResponse(content=b"new pdf content")

    monkeypatch.setattr(source_loader.requests, "get", fake_get)

    result = source_loader.download_pdf(pdf, tmp_path)

    assert result == tmp_path / "1_kurs.pdf"
    assert result.read_bytes() == b"new pdf content"
    assert calls == {
        "url": "https://cs.msu.ru/files/1_kurs.pdf",
        "timeout": 30,
    }