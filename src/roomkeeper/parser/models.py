from dataclasses import dataclass


@dataclass(frozen=True)
class SchedulePdf:
    """PDF-файл с расписанием на сайте ВМК."""

    title: str
    url: str
    filename: str


@dataclass(frozen=True)
class OccupancySlot:
    """Одна запись о занятости аудитории."""

    source_file: str
    weekday: str
    start_time: str
    end_time: str
    room: str
    raw_line: str
