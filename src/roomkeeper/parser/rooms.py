import re

KNOWN_ROOMS = frozenset(
    {
        "64",
        "71",
        "72",
        "73",
        "230",
        "247-а",
        "247-в",
        "248",
        "248-а",
        "371",
        "503",
        "504",
        "505",
        "506",
        "507",
        "508",
        "510",
        "515",
        "523",
        "524",
        "526-б",
        "527",
        "549",
        "551",
        "570",
        "571",
        "574",
        "577",
        "579",
        "580",
        "582",
        "582-а",
        "589",
        "604",
        "605",
        "606",
        "607",
        "609",
        "612",
        "613",
        "615",
        "616",
        "624",
        "637",
        "642",
        "645",
        "653",
        "658",
        "659",
        "660",
        "671",
        "682",
        "685",
        "687",
        "696",
        "702",
        "706",
        "707",
        "713",
        "727",
        "729",
        "731",
        "735",
        "736",
        "740",
        "758",
        "778",
        "779",
        "780",
        "782",
        "783",
        "785",
        "786",
        "787",
        "790",
        "819-а",
        "МЗ-0",
        "МЗ-1",
        "МЗ-2",
        "МЗ-3",
        "МЗ-4",
        "П-5",
        "П-6",
        "П-8",
        "П-8а",
        "П-11",
        "П-12",
        "П-13",
        "П-14",
    }
)


ROOM_CANDIDATE_RE = re.compile(
    r"""
    (?:
        П\s*[-–]?\s*\d{1,2}[а-яА-Я]?
        |
        МЗ\s*[-–]\s*\d{1,2}
        |
        (?<!\d)[1-9]\d{1,2}(?:\s*[-–]\s*[а-яА-Я]|[а-яА-Я])?(?!\d)
    )
    """,
    re.VERBOSE,
)


def normalize_room(room: str) -> str:
    """Приводит название аудитории к единому виду."""
    room = room.strip()
    room = room.replace("–", "-")
    room = re.sub(r"\s+", "", room)

    if room.lower().startswith("п"):
        number = re.sub(r"^[пП]-?", "", room)
        return "П-" + number.lower()

    if room.lower().startswith("мз-"):
        number = room.split("-", 1)[1]
        return "МЗ-" + number

    room = re.sub(r"^(\d+)([А-Яа-я])$", r"\1-\2", room)

    if re.fullmatch(r"\d{2,3}-[А-Яа-я]", room):
        return room[:-1] + room[-1].lower()

    return room


def extract_rooms_from_line(line: str) -> list[str]:
    """Извлекает из строки только реальные аудитории ВМК."""
    result: list[str] = []

    for match in ROOM_CANDIDATE_RE.finditer(line):
        room = normalize_room(match.group(0))

        if room in KNOWN_ROOMS and room not in result:
            result.append(room)

    return result