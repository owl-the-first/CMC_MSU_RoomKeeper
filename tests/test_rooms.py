from roomkeeper.parser.rooms import KNOWN_ROOMS, extract_rooms_from_line, normalize_room


def test_extract_rooms_ignores_group_numbers_and_fake_rooms() -> None:
    line = "138 141 142 203 204 207 208 209 211 213 214 215 216 217 241 242"

    assert extract_rooms_from_line(line) == []


def test_extract_rooms_keeps_only_known_vmk_rooms() -> None:
    line = "64 71 72 73 230 234 247-а 247-в 248 248-а 320 321"

    assert extract_rooms_from_line(line) == [
        "64",
        "71",
        "72",
        "73",
        "230",
        "247-а",
        "247-в",
        "248",
        "248-а",
    ]


def test_extract_rooms_keeps_projector_and_mz_rooms() -> None:
    line = "П-5 П-6 П-8 П-8а П-11 П-12 П-13 П-14 МЗ-0 МЗ-1 МЗ-2 МЗ-3 МЗ-4"

    assert extract_rooms_from_line(line) == [
        "П-5",
        "П-6",
        "П-8",
        "П-8а",
        "П-11",
        "П-12",
        "П-13",
        "П-14",
        "МЗ-0",
        "МЗ-1",
        "МЗ-2",
        "МЗ-3",
        "МЗ-4",
    ]


def test_known_rooms_count() -> None:
    assert len(KNOWN_ROOMS) == 89


def test_normalize_room() -> None:
    assert normalize_room("П - 13") == "П-13"       # проверяем удаление пробелов и дефис
    assert normalize_room("МЗ – 1") == "МЗ-1"       # проверяем замену длинного тире на обычный дефис
    assert normalize_room("582-А") == "582-а"       # проверяем приведение буквы в номере аудитории к нижнему регистру


def test_extract_rooms_from_line() -> None:
    # строка с несколькими аудиториями разных форматов
    line = "Новикова Н.М. 731, 248, МЗ-1, П-13"

    # проверяем, что все аудитории найдены в правильном порядке
    assert extract_rooms_from_line(line) == ["731", "248", "МЗ-1", "П-13"]


def test_extract_rooms_does_not_take_time_as_room() -> None:
    # в строке есть время, которое не должно считаться аудиторией
    line = "8.45 - 10.20 Математический анализ П-6"

    # проверяем, что функция достала только аудиторию
    assert extract_rooms_from_line(line) == ["П-6"]


def test_extract_rooms_does_not_take_group_names_as_rooms() -> None:
    line = "101-м 103-в 110-к 181-д 320 321"

    assert extract_rooms_from_line(line) == []


def test_extract_rooms_keeps_known_letter_rooms() -> None:
    line = "Занятие проходит в 247-а, 247-в, 526-б, 582-а, 819-а"

    assert extract_rooms_from_line(line) == [
        "247-а",
        "247-в",
        "526-б",
        "582-а",
        "819-а",
    ]