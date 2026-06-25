"""Общие настройки pytest."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

LOCALES_DIR = Path(__file__).resolve().parent.parent / "src" / "roomkeeper" / "locales"


def _needs_i18n_compile() -> bool:
    """Проверяет, нужно ли пересобрать бинарные каталоги переводов."""
    for po_file in LOCALES_DIR.glob("*/LC_MESSAGES/messages.po"):
        mo_file = po_file.with_suffix(".mo")
        if not mo_file.exists():
            return True
        if mo_file.stat().st_mtime < po_file.stat().st_mtime:
            return True

    return False


def _compile_i18n_catalogs() -> None:
    """Компилирует .po-файлы в .mo для gettext."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "babel.messages.frontend",
            "compile",
            "-d",
            str(LOCALES_DIR),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Не удалось скомпилировать переводы: {message}")


def pytest_configure() -> None:
    """Готовит переводы перед запуском тестов."""
    if _needs_i18n_compile():
        _compile_i18n_catalogs()
