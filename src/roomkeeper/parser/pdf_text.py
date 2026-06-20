from pathlib import Path

import pdfplumber


def extract_lines_from_pdf(pdf_path: Path) -> list[str]:
    """Извлечение строки текста из PDF-файла."""
    lines: list[str] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""

            for line in text.splitlines():
                line = line.strip()
                if line:
                    lines.append(line)

    return lines
