from pathlib import Path

from roomkeeper.parser.pdf_text import extract_lines_from_pdf


RAW_DIR = Path("data/raw")


def main() -> None:
    pdf_files = sorted(RAW_DIR.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found. Run scripts/download_schedule_pdfs.py first.")
        return

    pdf_path = pdf_files[0]
    lines = extract_lines_from_pdf(pdf_path)

    print(f"file: {pdf_path}")
    print(f"lines: {len(lines)}")
    print()

    for line in lines[:40]:
        print(line)


if __name__ == "__main__":
    main()
