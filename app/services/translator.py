# utils/translator.py

from googletrans import Translator

__translator = Translator()


async def translate(text: str) -> dict[str, str]:
    """
    Determines whether text is Japanese or English, and returns the original and translated text.

    Args:
        text (str): Original string.
    Returns:
        dict: Original and translated strings.
    """

    translate: dict[str, str] = {"en": "", "ja": ""}
    if await is_english(text):
        translate["en"] = text
        translate["ja"] = await translate_to_japanese(text)
    else:
        translate["en"] = await translate_to_english(text)
        translate["ja"] = text

    return translate


async def is_english(text: str) -> bool:
    """
    Checks whether text is English.

    Args:
        text (str): The string to check.
    Returns:
        bool: True if English, False if not.
    """

    detection = await __translator.detect(text)
    return detection.lang == "en"


async def translate_to_japanese(text: str) -> str:
    """
    Translate text into Japanese.

    Args:
        text (str): The string to translate.
    Returns:
        str: The translated string.
    """

    translation = await __translator.translate(text, dest="ja")
    return translation.text


async def translate_to_english(text: str) -> str:
    """
    Translate text into English.

    Args:
        text (str): The string to translate.
    Returns:
        str: The translated string.
    """

    translation = await __translator.translate(text, dest="en")
    return translation.text
