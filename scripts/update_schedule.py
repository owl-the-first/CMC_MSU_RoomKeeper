import json
from dataclasses import asdict
from pathlib import Path

from roomkeeper.parser.pdf_text import extract_lines_from_pdf
from roomkeeper.parser.schedule_parser import parse_lines
from roomkeeper.parser.source_loader import download_pdf, find_schedule_pdfs

RAW_DIR = Path("data/raw")                          # каталог для хранения скачанных PDF-файлов
PARSED_DIR = Path("data/parsed")                    # каталог для хранения результатов парсинга
OUTPUT_FILE = PARSED_DIR / "schedule_slots.json"    # файл, в который сохраняется итоговое расписание


def main() -> None:
    """Скачивает, парсит и сохраняет расписание."""
    # получаем список PDF-файлов с расписанием
    pdfs = find_schedule_pdfs()

    # выводим количество найденных файлов
    print(f"Found schedule PDFs: {len(pdfs)}")

    # здесь будут храниться все записи о занятиях
    all_slots = []

    # последовательно обрабатываем каждый PDF-файл
    for pdf in pdfs:
        # скачиваем PDF-файл в директорию data/raw
        pdf_path = download_pdf(pdf, RAW_DIR)
        print(f"downloaded: {pdf_path}")

        # извлекаем текст из PDF
        lines = extract_lines_from_pdf(pdf_path)

        # преобразуем строки текста в записи о занятиях
        slots = parse_lines(lines, source_file=pdf_path.name)

        # выводим количество строк и найденных записей
        print(f"  lines: {len(lines)}")
        print(f"  slots: {len(slots)}")

        # добавляем записи в общий список
        all_slots.extend(slots)

    # создаем директорию data/parsed при необходимости
    PARSED_DIR.mkdir(parents=True, exist_ok=True)

    # преобразуем объекты OccupancySlot в словари
    data = [asdict(slot) for slot in all_slots]

    # сохраняем результат в JSON-файл
    OUTPUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # выводим общее количество найденных записей
    print()
    print(f"Total slots: {len(data)}")

    # выводим путь к сохраненному JSON-файлу
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
