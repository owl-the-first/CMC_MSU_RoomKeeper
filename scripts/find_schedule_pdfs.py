from roomkeeper.parser.source_loader import find_schedule_pdfs


def main() -> None:
    pdfs = find_schedule_pdfs()

    print(f"Found schedule PDFs: {len(pdfs)}")

    for pdf in pdfs:
        print(f"- {pdf.title}")
        print(f"  file: {pdf.filename}")
        print(f"  url:  {pdf.url}")


if __name__ == "__main__":
    main()
