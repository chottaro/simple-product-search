import re
from typing import Callable


def find_jan_code(targets: list[str]) -> str:
    """
    Extract the JAN code (13, 8 digits) from targets.
    Because JAN codes are checked and passed values are returned as character strings, unexpected values may be returned.

    Args:
        targets (list): Strings from which to extract the JAN code.
    Returns:
        str: JAN code (13, 8 digits).
    """

    get_candidates: Callable[[str, str], list[str]] = lambda regex, target: re.findall(
        regex, target
    )

    jan_code: str = ""
    for target in targets:
        # 正規表現で8桁 or 13桁の数字列を抽出
        candidates: list[str] = get_candidates(r"\b\d{8}\b|\b\d{13}\b", target)
        jan_codes: list[str] = [code for code in candidates if __is_valid_jan(code.zfill(13))]

        if len(jan_codes) > 0:
            jan_code = jan_codes[0]
            break
        else:
            # 前後空白ありの数値で取得できなかった場合はJANと明記している個所を抜き出す
            jan_codes = get_candidates(r"JAN\D*?(\d{8}|\d{13})\D", target)
            jan_code = "" if len(jan_codes) == 0 else jan_codes[0]
            if jan_code != "":
                break

    return jan_code


def __is_valid_jan(code: str) -> bool:
    """
    Check for a 13 digit jan code.

    Args:
        code (str): String to validate.
    Returns:
        bool: True if the JAN code qualifies as, false otherwise.
    """

    if not code.isdigit() or len(code) != 13:
        return False
    calculated_check_digit: int = __calculate_jan_check_digit(code[:-1], 12)
    return int(code[-1]) == calculated_check_digit


def __calculate_jan_check_digit(code: str, code_len: int) -> int:
    """
    Calculate check digits for JAN codes.

    Args:
        code (str): Code with the last digit excluded.
        code_len (int): JAN code size.
    Returns:
        int: Calculated Check Digits.
    """

    if not code.isdigit() or len(code) != code_len:
        return -1

    total = sum(int(d) if (i % 2 == 0) else int(d) * 3 for i, d in enumerate(code))
    remainder = total % 10
    return 0 if remainder == 0 else 10 - remainder
