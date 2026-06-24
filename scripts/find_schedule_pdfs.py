from roomkeeper.parser.source_loader import find_schedule_pdfs


def main() -> None:
    """Показывает найденные PDF-файлы с расписанием."""
    # ищем PDF-файлы расписания
    pdfs = find_schedule_pdfs()

    # выводим количество найденных файлов
    print(f"Found schedule PDFs: {len(pdfs)}")

    # выводим информацию о каждом файле
    for pdf in pdfs:
        print(f"- {pdf.title}")
        print(f"  file: {pdf.filename}")
        print(f"  url:  {pdf.url}")


if __name__ == "__main__":
    main()
