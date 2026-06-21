from roomkeeper.parser.schedule_parser import parse_lines


def test_parse_lines_extracts_slots() -> None:
    lines = [
        "Понедельник 101 102 103",
        "8.45 - 10.20",
        "Алгебра и геометрия П-13",
        "Практикум на ЭВМ 605",
        "Вторник 101 102 103",
        "10.30 - 12.05 Дискретная математика МЗ-1, 731",
    ]

    # запускаем парсер расписания
    slots = parse_lines(lines, source_file="test.pdf")

    assert len(slots) == 4              # должны получить 4 записи о занятиях

    # проверяем первую запись
    assert slots[0].weekday == "Понедельник"
    assert slots[0].start_time == "08:45"
    assert slots[0].end_time == "10:20"
    assert slots[0].room == "П-13"

    assert slots[1].room == "605"       # проверяем аудиторию второго занятия

    # проверяем запись для вторника
    assert slots[2].weekday == "Вторник"
    assert slots[2].start_time == "10:30"
    assert slots[2].end_time == "12:05"
    assert slots[2].room == "МЗ-1"

    assert slots[3].room == "731"       # проверяем последнюю найденную аудиторию
