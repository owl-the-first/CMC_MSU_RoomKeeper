from pathlib import Path

from roomkeeper.parser.pdf_text import extract_lines_from_pdf

# директория с PDF-файлами
RAW_DIR = Path("data/raw")


def main() -> None:
    # получаем список PDF
    pdf_files = sorted(RAW_DIR.glob("*.pdf"))

    # если файлов нет -> завершаем программу
    if not pdf_files:
        print("No PDF files found. Run scripts/download_schedule_pdfs.py first.")
        return

    pdf_path = pdf_files[0]                         # берем первый PDF-файл
    lines = extract_lines_from_pdf(pdf_path)        # извлекаем строки текста

    # выводим информацию о файле
    print(f"file: {pdf_path}")
    print(f"lines: {len(lines)}")
    print()

    # показываем первые строки
    for line in lines[:40]:
        print(line)


if __name__ == "__main__":
    main()
