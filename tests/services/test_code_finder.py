from app.services import code_finder


def test_find_jan_code_8_digits_ok() -> None:
    jan_codes: list[str] = ["49012347"]
    assert code_finder.find_jan_code(jan_codes) == jan_codes[0]

    jan_codes = ["49968712", "49012347"]
    assert code_finder.find_jan_code(jan_codes) == jan_codes[0]


def test_find_jan_code_8_digits_ng() -> None:
    jan_codes: list[str] = ["00000001"]
    assert code_finder.find_jan_code(jan_codes) == ""

    jan_codes = ["00000001", "00000002"]
    assert code_finder.find_jan_code(jan_codes) == ""


def test_find_jan_code_8_digits_partially_ok() -> None:
    jan_codes: list[str] = ["49968712", "00000001"]
    assert code_finder.find_jan_code(jan_codes) == jan_codes[0]

    jan_codes = ["00000001", "49012347"]
    assert code_finder.find_jan_code(jan_codes) == jan_codes[1]


def test_find_jan_code_13_digits_ok() -> None:
    jan_codes: list[str] = ["4902370550733"]
    assert code_finder.find_jan_code(jan_codes) == jan_codes[0]

    jan_codes = ["4902370548501", "4902370550733"]
    assert code_finder.find_jan_code(jan_codes) == jan_codes[0]


def test_find_jan_code_13_digits_ng() -> None:
    jan_codes: list[str] = ["0000000000001"]
    assert code_finder.find_jan_code(jan_codes) == ""

    jan_codes = ["0000000000001", "0000000000002"]
    assert code_finder.find_jan_code(jan_codes) == ""


def test_find_jan_code_13_digits_partially_ok() -> None:
    jan_codes: list[str] = ["4902370550733", "0000000000001"]
    assert code_finder.find_jan_code(jan_codes) == jan_codes[0]

    jan_codes = ["0000000000001", "4902370550733"]
    assert code_finder.find_jan_code(jan_codes) == jan_codes[1]
