from pathlib import Path

import pdfplumber


def extract_lines_from_pdf(pdf_path: Path) -> list[str]:
    """Извлечение строки текста из PDF-файла."""
    # список строк из PDF
    lines: list[str] = []

    # открываем PDF
    with pdfplumber.open(pdf_path) as pdf:

        # читаем подряд страницы
        for page in pdf.pages:
            text = page.extract_text() or ""        # получаем текст страницы

            # разбиваем текст на строки
            for line in text.splitlines():
                line = line.strip()                 # удаляем лишние пробелы
                if line:                            # добавляем только непустые строки
                    lines.append(line)

    # возвращаем список строк
    return lines
