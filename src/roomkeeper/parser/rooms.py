import re

ROOM_RE = re.compile(
    r"""
    (?:
        П\s*[-–]\s*\d{1,2}[а-яА-Я]?
        |
        МЗ\s*[-–]\s*\d{1,2}
        |
        (?<!\d)[1-9]\d{2}(?:[-–]?[а-яА-Я])?(?!\d)
        |
        (?<!\d)7[1-9](?!\d)
    )
    """,
    re.VERBOSE,
)


def normalize_room(room: str) -> str:
    room = room.strip()
    room = room.replace("–", "-")
    room = re.sub(r"\s+", "", room)

    if room.lower().startswith("п-"):
        number = room.split("-", 1)[1]
        return "П-" + number.lower()

    if room.lower().startswith("мз-"):
        number = room.split("-", 1)[1]
        return "МЗ-" + number

    room = re.sub(r"^(\d+)([А-Яа-я])$", r"\1-\2", room)

    if re.fullmatch(r"\d{3}-[А-Яа-я]", room):
        return room[:-1] + room[-1].lower()

    return room


def extract_rooms_from_line(line: str) -> list[str]:
    rooms = [normalize_room(match.group(0)) for match in ROOM_RE.finditer(line)]

    result: list[str] = []

    for room in rooms:
        if room not in result:
            result.append(room)

    return result
