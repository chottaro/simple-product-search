from unittest.mock import AsyncMock, Mock, patch

from requests.exceptions import HTTPError

from app.search import rakuten


@patch(
    "app.search.rakuten.get_requests",
    return_value={
        "Items": [
            {
                "itemName": "テスト商品 1",
                "itemPrice": 1111,
                "itemUrl": "https://example.com/4902370550733/item1",
                "mediumImageUrls": [
                    "https://example.com/image1-1.jpg",
                    "https://example.com/image1-2.jpg",
                ],
                "itemCaption": "テスト",
            },
            {
                "itemName": "テスト商品 2",
                "itemPrice": 2222,
                "itemUrl": "https://example.com/item2",
                "mediumImageUrls": [],
                "itemCaption": "JAN　4902370550733",
            },
        ],
        "page": 1,
    },
)
def test_search_rakuten_items_keyword_exists_code(mock_get_requests: AsyncMock) -> None:

    keywords = ["mock_keyword"]
    option = {"search_type": 0, "search_result_limit": 2}

    results = rakuten.search_rakuten_items(keywords, option)

    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]["jan_code"] == "4902370550733"
    assert results[0]["product_name"] == "テスト商品 1"
    assert results[0]["price"] == 1111
    assert results[0]["url"] == "https://example.com/4902370550733/item1"
    assert results[0]["image_url"] == "https://example.com/image1-1.jpg"
    assert results[1]["jan_code"] == "4902370550733"
    assert results[1]["product_name"] == "テスト商品 2"
    assert results[1]["price"] == 2222
    assert results[1]["url"] == "https://example.com/item2"
    assert results[1]["image_url"] == ""
    assert mock_get_requests.called


@patch(
    "app.search.rakuten.get_requests",
    return_value={
        "Items": [
            {
                "itemName": "テスト商品 1",
                "itemPrice": 1111,
                "itemUrl": "https://example.com/item1",
                "mediumImageUrls": [
                    "https://example.com/49012347/image1-1.jpg",
                    "https://example.com/image1-2.jpg",
                ],
                "itemCaption": "テスト",
            },
            {
                "itemName": "テスト商品 49012347 2",
                "itemPrice": 2222,
                "itemUrl": "https://example.com/item2",
                "mediumImageUrls": [],
                "itemCaption": "テスト",
            },
        ],
        "page": 1,
    },
)
def test_search_rakuten_jan_code_exists_code(mock_get_requests: AsyncMock) -> None:

    keywords = ["49012347"]
    option = {"search_type": 1, "search_result_limit": 2}

    results = rakuten.search_rakuten_items(keywords, option)

    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]["jan_code"] == "49012347"
    assert results[0]["product_name"] == "テスト商品 1"
    assert results[0]["price"] == 1111
    assert results[0]["url"] == "https://example.com/item1"
    assert results[0]["image_url"] == "https://example.com/49012347/image1-1.jpg"
    assert results[1]["jan_code"] == "49012347"
    assert results[1]["product_name"] == "テスト商品 49012347 2"
    assert results[1]["price"] == 2222
    assert results[1]["url"] == "https://example.com/item2"
    assert results[1]["image_url"] == ""
    assert mock_get_requests.called


@patch(
    "app.search.rakuten.get_requests",
    return_value={
        "Items": [
            {
                "itemName": "テスト商品 1",
                "itemPrice": 1111,
                "itemUrl": "https://example.com/9999999999999/item1",
                "mediumImageUrls": [
                    "https://example.com/image1-1.jpg",
                    "https://example.com/image1-2.jpg",
                ],
                "itemCaption": "テスト",
            },
            {
                "itemName": "テスト商品 2",
                "itemPrice": 2222,
                "itemUrl": "https://example.com/item2",
                "mediumImageUrls": [],
                "itemCaption": "JAN　9999999999999",
            },
        ],
        "page": 1,
    },
)
def test_search_rakuten_items_keyword_not_exists_code(mock_get_requests: AsyncMock) -> None:

    keywords = ["mock_keyword"]
    option = {"search_type": 0, "search_result_limit": 2}

    results = rakuten.search_rakuten_items(keywords, option)

    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]["jan_code"] == ""
    assert results[0]["product_name"] == "テスト商品 1"
    assert results[0]["price"] == 1111
    assert results[0]["url"] == "https://example.com/9999999999999/item1"
    assert results[0]["image_url"] == "https://example.com/image1-1.jpg"
    assert results[1]["jan_code"] == ""
    assert results[1]["product_name"] == "テスト商品 2"
    assert results[1]["price"] == 2222
    assert results[1]["url"] == "https://example.com/item2"
    assert results[1]["image_url"] == ""
    assert mock_get_requests.called


@patch(
    "app.search.rakuten.get_requests",
    return_value={
        "Items": [],
        "page": 1,
    },
)
def test_search_rakuten_no_data(mock_get_requests: AsyncMock) -> None:

    keywords = ["mock_keyword"]
    option = {"search_type": 1, "search_result_limit": 2}

    results = rakuten.search_rakuten_items(keywords, option)

    assert isinstance(results, list)
    assert len(results) == 0
    assert mock_get_requests.called


@patch("app.search.rakuten.get_requests")
def test_search_rakuten_items_raise_exception(mock_get_requests: AsyncMock) -> None:
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = HTTPError("Unauthorized")
    mock_response.get.return_value = []
    mock_get_requests.return_value = mock_response

    keywords = ["mock_keyword"]
    option = {"search_type": 1, "search_result_limit": 2}

    results = rakuten.search_rakuten_items(keywords, option)

    assert isinstance(results, list)
    assert len(results) == 0
    assert mock_get_requests.called
