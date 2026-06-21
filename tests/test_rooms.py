from roomkeeper.parser.rooms import extract_rooms_from_line, normalize_room


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
