from unittest.mock import AsyncMock, Mock, patch

from requests.exceptions import HTTPError

from app.search import yahoo


@patch(
    "app.search.yahoo.get_requests",
    return_value={
        "hits": [
            {
                "name": "テスト商品 1",
                "price": 1111,
                "url": "https://example.com/item1",
                "image": {
                    "small": "https://example.com/image1-1.jpg",
                    "medium": "https://example.com/image1-2.jpg",
                },
                "janCode": "4902370550733",
            },
            {
                "name": "テスト商品 2",
                "price": 2222,
                "url": "https://example.com/item2",
                "image": {},
                "janCode": "",
            },
        ],
    },
)
def test_search_yahoo_items_keyword_exists_code(mock_get_requests: AsyncMock) -> None:

    keyword = "mock_keyword"
    option = {"search_type": 0, "search_result_limit": 2}

    results = yahoo.search_yahoo_items_by_keyword(keyword, option)

    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]["jan_code"] == "4902370550733"
    assert results[0]["product_name"] == "テスト商品 1"
    assert results[0]["price"] == 1111
    assert results[0]["url"] == "https://example.com/item1"
    assert results[0]["image_url"] == "https://example.com/image1-2.jpg"
    assert results[1]["jan_code"] == ""
    assert results[1]["product_name"] == "テスト商品 2"
    assert results[1]["price"] == 2222
    assert results[1]["url"] == "https://example.com/item2"
    assert results[1]["image_url"] == None
    assert mock_get_requests.called


@patch(
    "app.search.yahoo.get_requests",
    return_value={
        "hits": [
            {
                "name": "テスト商品 1",
                "price": 1111,
                "url": "https://example.com/item1",
                "image": {
                    "small": "https://example.com/image1-1.jpg",
                    "medium": "https://example.com/image1-2.jpg",
                },
                "janCode": "49012347",
            },
            {
                "name": "テスト商品 2",
                "price": 2222,
                "url": "https://example.com/item2",
                "image": {},
                "janCode": "49012347",
            },
        ],
    },
)
def test_search_yahoo_jan_code_exists_code(mock_get_requests: AsyncMock) -> None:

    keywords = ["49012347"]
    option = {"search_type": 1, "search_result_limit": 2}

    results = yahoo.search_yahoo_items_by_jan_code(keywords, option)

    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]["jan_code"] == "49012347"
    assert results[0]["product_name"] == "テスト商品 1"
    assert results[0]["price"] == 1111
    assert results[0]["url"] == "https://example.com/item1"
    assert results[0]["image_url"] == "https://example.com/image1-2.jpg"
    assert results[1]["jan_code"] == "49012347"
    assert results[1]["product_name"] == "テスト商品 2"
    assert results[1]["price"] == 2222
    assert results[1]["url"] == "https://example.com/item2"
    assert results[1]["image_url"] == None
    assert mock_get_requests.called


@patch(
    "app.search.yahoo.get_requests",
    return_value={
        "hits": [],
    },
)
def test_search_yahoo_items_keyword_no_data(mock_get_requests: AsyncMock) -> None:

    keyword = "mock_keyword"
    option = {"search_type": 0, "search_result_limit": 2}

    results = yahoo.search_yahoo_items_by_keyword(keyword, option)

    assert isinstance(results, list)
    assert len(results) == 0
    assert mock_get_requests.called


@patch(
    "app.search.yahoo.get_requests",
    return_value={
        "hits": [],
    },
)
def ttest_search_yahoo_jan_code_no_data(mock_get_requests: AsyncMock) -> None:

    keywords = ["9999999999999"]
    option = {"search_type": 1, "search_result_limit": 2}

    results = yahoo.search_yahoo_items_by_jan_code(keywords, option)

    assert isinstance(results, list)
    assert len(results) == 0
    assert mock_get_requests.called


@patch("app.search.yahoo.get_requests")
def test_search_yahoo_items_raise_exception(mock_get_requests: AsyncMock) -> None:
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = HTTPError("Unauthorized")
    mock_response.get.return_value = []
    mock_get_requests.return_value = mock_response

    keywords = ["mock_keyword"]
    option = {"search_type": 1, "search_result_limit": 2}

    results = yahoo._search_yahoo_items(keywords, option)

    assert isinstance(results, list)
    assert len(results) == 0
    assert mock_get_requests.called
