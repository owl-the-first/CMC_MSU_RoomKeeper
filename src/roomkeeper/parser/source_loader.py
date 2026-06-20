from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from roomkeeper.parser.models import SchedulePdf


SCHEDULE_PAGE_URL = "https://cs.msu.ru/studies/schedule"


def fetch_html(url: str = SCHEDULE_PAGE_URL) -> str:
    """Скачивание HTML-страницы расписания."""
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.text


def _filename_from_url(url: str) -> str:
    """Изъятие имени файла из URL."""
    path = urlparse(url).path
    return Path(path).name


def _is_schedule_pdf(title: str, url: str) -> bool:
    """
    Проверка: похож ли PDF на файл с расписанием.

    На странице с расписанием есть разные PDF. Нужны именно
    файлы с расписанием курсов. В названии файла - 'kurs'.
    """
    text = f"{title} {url}".lower()

    if not url.lower().endswith(".pdf"):
        return False

    if "chetnost" in text or "четность" in text:
        return False

    return "kurs" in text or "raspis" in text or "магистратура" in text


def find_schedule_pdfs(url: str = SCHEDULE_PAGE_URL) -> list[SchedulePdf]:
    """Поиск PDF-файлов с расписанием на странице."""
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    result: list[SchedulePdf] = []

    for link in soup.find_all("a"):
        href = link.get("href")
        if not href:
            continue

        full_url = urljoin(url, href)
        title = link.get_text(" ", strip=True)
        filename = _filename_from_url(full_url)

        if _is_schedule_pdf(title, full_url):
            result.append(
                SchedulePdf(
                    title=title or filename,
                    url=full_url,
                    filename=filename,
                )
            )

    return result


def download_pdf(pdf: SchedulePdf, output_dir: Path, force: bool = False) -> Path:
    """Скачивание одного PDF-файла с расписанием."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / pdf.filename

    if output_path.exists() and not force:
        return output_path

    response = requests.get(pdf.url, timeout=30)
    response.raise_for_status()

    output_path.write_bytes(response.content)
    return output_path
