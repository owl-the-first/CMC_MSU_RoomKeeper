from dataclasses import dataclass


# Описание PDF-файла с расписанием; для поиска и скачивания файлов
@dataclass(frozen=True)
class SchedulePdf:
    """PDF-файл с расписанием на сайте ВМК."""

    title: str          # название ссылки на странице
    url: str            # полный адрес PDF-файла
    filename: str       # имя файла для сохранения


# Описание одной записи о занятости аудитории; используется после парсинга расписания
@dataclass(frozen=True)
class OccupancySlot:
    """Одна запись о занятости аудитории."""

    source_file: str        # из какого файла получена запись
    weekday: str            # день недели
    start_time: str         # время начала пары
    end_time: str           # время окончания пары
    room: str               # номер аудитории
    raw_line: str           # исходная строка (из PDF)
