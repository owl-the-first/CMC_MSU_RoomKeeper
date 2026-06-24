"""Tests for command line entry points."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from roomkeeper.cli import bot, db_stats, import_schedule, init_db, update_schedule


def test_bot_cli_runs_bot(monkeypatch) -> None:
    """Проверяем, что CLI-команда запускает Telegram-бота."""

    calls = {}

    def fake_run_bot() -> None:
        calls["run_bot"] = True

    monkeypatch.setattr(bot, "run_bot", fake_run_bot)

    bot.main()

    assert calls == {"run_bot": True}


def test_init_db_cli_creates_tables(monkeypatch, capsys) -> None:
    """Проверяем, что CLI-команда создает таблицы базы данных."""

    calls = {}

    def fake_create_tables() -> None:
        calls["create_tables"] = True

    monkeypatch.setattr(init_db, "create_tables", fake_create_tables)
    monkeypatch.setattr(init_db, "DEFAULT_DATABASE_URL", "sqlite:///test.db")

    init_db.main()

    output = capsys.readouterr().out

    assert calls == {"create_tables": True}
    assert "Database initialized: sqlite:///test.db" in output


def test_import_schedule_cli_imports_json(monkeypatch, tmp_path: Path, capsys) -> None:
    """Проверяем, что CLI-команда импортирует расписание из JSON."""

    schedule_json = tmp_path / "schedule_slots.json"
    result = SimpleNamespace(
        imported_slots=3,
        rooms_count=2,
        schedule_slots_count=3,
    )
    calls = {}

    def fake_import_schedule_slots(path: Path):
        calls["path"] = path
        return result

    monkeypatch.setattr(import_schedule, "SCHEDULE_JSON", schedule_json)
    monkeypatch.setattr(import_schedule, "DEFAULT_DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setattr(
        import_schedule,
        "import_schedule_slots",
        fake_import_schedule_slots,
    )

    import_schedule.main()

    output = capsys.readouterr().out

    assert calls == {"path": schedule_json}
    assert "Database: sqlite:///test.db" in output
    assert "Imported slots: 3" in output
    assert "Rooms in DB: 2" in output
    assert "Schedule slots in DB: 3" in output


def test_update_schedule_cli_downloads_parses_and_saves_json(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    """Проверяем скачивание, парсинг и сохранение расписания через CLI."""

    raw_dir = tmp_path / "raw"
    parsed_dir = tmp_path / "parsed"
    output_file = parsed_dir / "schedule_slots.json"
    pdf = SimpleNamespace(
        title="1 курс",
        url="https://example.com/1.pdf",
        filename="1.pdf",
    )
    slot = object()
    calls = {}

    def fake_find_schedule_pdfs(url: str):
        calls["schedule_url"] = url
        return [pdf]

    def fake_download_pdf(pdf_info, target_dir: Path) -> Path:
        calls["pdf"] = pdf_info
        calls["target_dir"] = target_dir
        return target_dir / "1.pdf"

    def fake_extract_lines_from_pdf(path: Path) -> list[str]:
        calls["pdf_path"] = path
        return ["Понедельник 605", "8.45-10.20"]

    def fake_parse_lines(lines: list[str], source: str):
        calls["lines"] = lines
        calls["source"] = source
        return [slot]

    def fake_asdict(parsed_slot) -> dict[str, str]:
        assert parsed_slot is slot
        return {
            "weekday": "Понедельник",
            "start_time": "8.45",
            "end_time": "10.20",
            "room_name": "605",
            "source": "1.pdf",
        }

    monkeypatch.setattr(update_schedule, "SCHEDULE_URL", "https://example.com/schedule")
    monkeypatch.setattr(update_schedule, "RAW_DIR", raw_dir)
    monkeypatch.setattr(update_schedule, "PARSED_DIR", parsed_dir)
    monkeypatch.setattr(update_schedule, "OUTPUT_FILE", output_file)
    monkeypatch.setattr(update_schedule, "find_schedule_pdfs", fake_find_schedule_pdfs)
    monkeypatch.setattr(update_schedule, "download_pdf", fake_download_pdf)
    monkeypatch.setattr(update_schedule, "extract_lines_from_pdf", fake_extract_lines_from_pdf)
    monkeypatch.setattr(update_schedule, "parse_lines", fake_parse_lines)
    monkeypatch.setattr(update_schedule, "asdict", fake_asdict)

    update_schedule.main()

    output = capsys.readouterr().out
    saved_data = json.loads(output_file.read_text(encoding="utf-8"))

    assert calls == {
        "schedule_url": "https://example.com/schedule",
        "pdf": pdf,
        "target_dir": raw_dir,
        "pdf_path": raw_dir / "1.pdf",
        "lines": ["Понедельник 605", "8.45-10.20"],
        "source": str(raw_dir / "1.pdf"),
    }
    assert saved_data == [
        {
            "weekday": "Понедельник",
            "start_time": "8.45",
            "end_time": "10.20",
            "room_name": "605",
            "source": "1.pdf",
        }
    ]
    assert "downloaded:" in output
    assert "saved slots: 1" in output
    assert f"output file: {output_file}" in output


def test_db_stats_cli_prints_database_statistics(monkeypatch, capsys) -> None:
    """Проверяем, что CLI-команда выводит статистику базы данных."""

    room = SimpleNamespace(name="605")
    slot = SimpleNamespace(
        weekday="Понедельник",
        start_time="8.45",
        end_time="10.20",
        room=room,
    )
    calls = {}

    class FakeScalars:
        """Тестовая замена результата session.scalars."""

        def __init__(self, values: list[object]) -> None:
            self.values = values

        def all(self) -> list[object]:
            return self.values

    class FakeSession:
        """Тестовая замена SQLAlchemy-сессии."""

        def __init__(self) -> None:
            self.scalars_calls = 0

        def __enter__(self) -> "FakeSession":
            return self

        def __exit__(self, exc_type, exc_value, traceback) -> None:
            return None

        def scalars(self, statement) -> FakeScalars:
            self.scalars_calls += 1

            if self.scalars_calls == 1:
                return FakeScalars([room])

            return FakeScalars([slot])

    class FakeSessionFactory:
        """Тестовая фабрика SQLAlchemy-сессий."""

        def __call__(self) -> FakeSession:
            return FakeSession()

    def fake_get_session_factory(database_url: str) -> FakeSessionFactory:
        calls["database_url"] = database_url
        return FakeSessionFactory()

    monkeypatch.setattr(db_stats, "DEFAULT_DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setattr(db_stats, "get_session_factory", fake_get_session_factory)
    monkeypatch.setattr(db_stats, "count_rooms", lambda session: 2)
    monkeypatch.setattr(db_stats, "count_schedule_slots", lambda session: 3)
    monkeypatch.setattr(db_stats, "count_bookings", lambda session: 1)

    db_stats.main()

    output = capsys.readouterr().out

    assert calls == {"database_url": "sqlite:///test.db"}
    assert "Database: sqlite:///test.db" in output
    assert "Rooms: 2" in output
    assert "Schedule slots: 3" in output
    assert "Bookings: 1" in output
    assert "First rooms:" in output
    assert "- 605" in output
    assert "First schedule slots:" in output
    assert "- Понедельник 8.45-10.20: 605" in output