import re


# регулярное выражение для поиска аудиторий в строке; ищет П-13, МЗ-1, 731, 582-А, 71 и похожие варианты
ROOM_RE = re.compile(
    r"""
    (?:
        П\s*[-–]\s*\d{1,2}
        |
        МЗ\s*[-–]\s*\d{1,2}
        |
        (?<![\d.])(?:[1-9]\d{2})(?:\s*[-–]\s*[а-яА-Я])?(?![\d.])
        |
        (?<![\d.])7[1-9](?![\d.])
    )
    """,
    re.VERBOSE,
)


def normalize_room(room: str) -> str:
    """Приводит аудиторию к единому виду."""
    room = room.strip()                     # убираем пробелы по краям строки
    room = room.replace("–", "-")           # заменяем длинное тире на обычный дефис
    room = re.sub(r"\s+", "", room)         # убираем все лишние пробелы внутри аудитории

    # приводим аудитории вида П-13 к единому написанию
    if room.lower().startswith("п-"):
        return "П-" + room.split("-", 1)[1]

    # приводим аудитории вида МЗ-1 к единому написанию
    if room.lower().startswith("мз-"):
        return "МЗ-" + room.split("-", 1)[1]

    # для аудиторий вида 582-А делаем букву маленькой
    if re.fullmatch(r"\d{3}-[А-Яа-я]", room):
        return room[:-1] + room[-1].lower()

    # если специальных правил нет, возвращаем как есть
    return room


def extract_rooms_from_line(line: str) -> list[str]:
    """Достаёт все аудитории из одной строки текста."""
    # ищем все совпадения и сразу формализуем аудитории
    rooms = [normalize_room(match.group(0)) for match in ROOM_RE.finditer(line)]

    # список аудиторий без повторов
    result: list[str] = []

    # добавляем аудитории в исходном порядке
    for room in rooms:
        if room not in result:
            result.append(room)

    # возвращаем итоговый список аудиторий
    return result
