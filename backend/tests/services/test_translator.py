from unittest.mock import AsyncMock, patch

import pytest

from app.services import translator


@pytest.mark.asyncio
@patch("app.services.translator.__translator.detect", new_callable=AsyncMock)
@patch("app.services.translator.__translator.translate", new_callable=AsyncMock)
async def test_translate_english_input(mock_translate: AsyncMock, mock_detect: AsyncMock) -> None:
    mock_detect.return_value.lang = "en"
    mock_translate.return_value.text = "こんにちは"

    result = await translator.translate("hello")

    assert result == {"en": "hello", "ja": "こんにちは"}
    mock_translate.assert_called_once_with("hello", dest="ja")


@pytest.mark.asyncio
@patch("app.services.translator.__translator.detect", new_callable=AsyncMock)
@patch("app.services.translator.__translator.translate", new_callable=AsyncMock)
async def test_translate_japanese_input(mock_translate: AsyncMock, mock_detect: AsyncMock) -> None:
    # 入力が日本語と判定されるようにモック
    mock_detect.return_value.lang = "ja"
    mock_translate.return_value.text = "hello"

    result = await translator.translate("こんにちは")

    assert result == {"en": "hello", "ja": "こんにちは"}
    mock_translate.assert_called_once_with("こんにちは", dest="en")
