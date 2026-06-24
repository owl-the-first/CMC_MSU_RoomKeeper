import json
from dataclasses import asdict
from pathlib import Path

from roomkeeper.parser.pdf_text import extract_lines_from_pdf
from roomkeeper.parser.schedule_parser import parse_lines

RAW_DIR = Path("data/raw")                              # каталог с исходными PDF-файлами
PARSED_DIR = Path("data/parsed")                        # каталог для сохранения результатов парсинга
OUTPUT_FILE = PARSED_DIR / "schedule_slots.json"        # файл, в который будет записан итоговый JSON


def main() -> None:
    """Парсит скачанные PDF-файлы расписания в JSON."""
    # получаем список PDF-файлов с расписанием
    pdf_files = sorted(RAW_DIR.glob("*.pdf"))

    # если PDF-файлы отсутствуют -> завершаем работу
    if not pdf_files:
        print("No PDF files found. Run scripts/download_schedule_pdfs.py first.")
        return

    all_slots = []          # здесь будут храниться все найденные записи

    # последовательно обрабатываем каждый PDF-файл
    for pdf_path in pdf_files:
        # показываем, какой файл сейчас разбирается
        print(f"parsing: {pdf_path}")

        # извлекаем строки текста из PDF
        lines = extract_lines_from_pdf(pdf_path)

        # преобразуем строки в список занятий
        slots = parse_lines(lines, source_file=pdf_path.name)

        # выводим количество строк и найденных записей
        print(f"  lines: {len(lines)}")
        print(f"  slots: {len(slots)}")

        # добавляем найденные записи к общему списку
        all_slots.extend(slots)

    # создаем директорию для результатов
    PARSED_DIR.mkdir(parents=True, exist_ok=True)

    # преобразуем dataclass-объекты в словари
    data = [asdict(slot) for slot in all_slots]

    # сохраняем результат в JSON-файл
    OUTPUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # выводим итоговое количество записей
    print()
    print(f"Total slots: {len(data)}")

    # показываем путь к сохранённому файлу
    print(f"Saved to: {OUTPUT_FILE}")

    print()
    print("First records:")

    # выводим несколько первых записей для проверки
    for item in data[:10]:
        print(
            f"{item['weekday']} "
            f"{item['start_time']}-{item['end_time']} "
            f"{item['room']} "
            f"({item['source_file']})"
        )


if __name__ == "__main__":
    main()
