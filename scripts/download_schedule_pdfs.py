from pathlib import Path

from roomkeeper.parser.source_loader import download_pdf, find_schedule_pdfs


RAW_DIR = Path("data/raw")


def main() -> None:
    pdfs = find_schedule_pdfs()

    print(f"PDF files to download: {len(pdfs)}")

    for pdf in pdfs:
        path = download_pdf(pdf, RAW_DIR)
        print(f"saved: {path}")


if __name__ == "__main__":
    main()
