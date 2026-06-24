"""Command line entry point for downloading and parsing schedule PDFs."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from roomkeeper.parser.pdf_text import extract_lines_from_pdf
from roomkeeper.parser.schedule_parser import parse_lines
from roomkeeper.parser.source_loader import download_pdf, find_schedule_pdfs

SCHEDULE_URL = "https://cs.msu.ru/studies/schedule"
RAW_DIR = Path("data/raw")
PARSED_DIR = Path("data/parsed")
OUTPUT_FILE = PARSED_DIR / "schedule_slots.json"


def main() -> None:
    """Download schedule PDFs, parse them and save schedule slots to JSON."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PARSED_DIR.mkdir(parents=True, exist_ok=True)

    pdfs = find_schedule_pdfs(SCHEDULE_URL)
    all_slots = []

    for pdf in pdfs:
        path = download_pdf(pdf, RAW_DIR)
        print(f"downloaded: {path}")

        lines = extract_lines_from_pdf(path)
        slots = parse_lines(lines, source=str(path))
        all_slots.extend(slots)

    data = [asdict(slot) for slot in all_slots]

    OUTPUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"saved slots: {len(all_slots)}")
    print(f"output file: {OUTPUT_FILE}")