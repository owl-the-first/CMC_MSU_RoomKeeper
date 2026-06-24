from pathlib import Path

from roomkeeper.parser.source_loader import download_pdf, find_schedule_pdfs

# директория для хранения исходных PDF
RAW_DIR = Path("data/raw")


def main() -> None:
    pdfs = find_schedule_pdfs()         # получаем список PDF-файлов

    print(f"PDF files to download: {len(pdfs)}")        # выводим количество файлов

    # скачиваем каждый файл
    for pdf in pdfs:
        path = download_pdf(pdf, RAW_DIR)
        print(f"saved: {path}")                 # выводим путь хранения каждого PDF-файла


if __name__ == "__main__":
    main()
