from unittest.mock import AsyncMock, Mock, patch

from requests.exceptions import HTTPError

from app.search import ebay


@patch("app.search.ebay._get_access_token", return_value="dummy_token")
@patch(
    "app.search.ebay.get_requests",
    return_value={
        "itemSummaries": [
            {
                "title": "Sample Item 1",
                "price": {"value": "11.11", "currency": "USD"},
                "itemWebUrl": "https://example.com/item1",
                "image": {
                    "imageUrl": "https://example.com/image1.jpg",
                },
            },
            {
                "title": "Sample Item 2",
                "price": {"value": "22.22", "currency": "USD"},
                "itemWebUrl": "https://example.com/item2",
                "image": {
                    "imageUrl": "https://example.com/image2.jpg",
                },
            },
        ]
    },
)
def test_search_ebay_items_keyword(mock_get_requests: AsyncMock, mock_get_token: AsyncMock) -> None:

    keywords = ["mock_keyword"]
    option = {"search_type": 0, "search_result_limit": 10}

    results = ebay.search_ebay_items(keywords, option)

    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]["jan_code"] == ""
    assert results[0]["product_name"] == "Sample Item 1"
    assert results[0]["price"] == 11.11
    assert results[0]["url"] == "https://example.com/item1"
    assert results[0]["image_url"] == "https://example.com/image1.jpg"
    assert results[1]["jan_code"] == ""
    assert results[1]["product_name"] == "Sample Item 2"
    assert results[1]["price"] == 22.22
    assert results[1]["url"] == "https://example.com/item2"
    assert results[1]["image_url"] == "https://example.com/image2.jpg"
    assert mock_get_requests.called
    assert mock_get_token.called


@patch("app.search.ebay._get_access_token", return_value="dummy_token")
@patch(
    "app.search.ebay.get_requests",
    return_value={
        "itemSummaries": [
            {
                "title": "Sample Item 1",
                "price": {"value": "11.11", "currency": "USD"},
                "itemWebUrl": "https://example.com/item1",
                "image": {
                    "imageUrl": "https://example.com/image1.jpg",
                },
            },
            {
                "title": "Sample Item 2",
                "price": {"value": "22.22", "currency": "USD"},
                "itemWebUrl": "https://example.com/item2",
                "image": {
                    "imageUrl": "https://example.com/image2.jpg",
                },
            },
        ]
    },
)
def test_search_ebay_items_jan_code(
    mock_get_requests: AsyncMock, mock_get_token: AsyncMock
) -> None:

    keywords = ["4902370550733"]
    option = {"search_type": 1, "search_result_limit": 10}

    results = ebay.search_ebay_items(keywords, option)

    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]["jan_code"] == "4902370550733"
    assert results[0]["product_name"] == "Sample Item 1"
    assert results[0]["price"] == 11.11
    assert results[0]["url"] == "https://example.com/item1"
    assert results[0]["image_url"] == "https://example.com/image1.jpg"
    assert results[1]["jan_code"] == "4902370550733"
    assert results[1]["product_name"] == "Sample Item 2"
    assert results[1]["price"] == 22.22
    assert results[1]["url"] == "https://example.com/item2"
    assert results[1]["image_url"] == "https://example.com/image2.jpg"
    assert mock_get_requests.called
    assert mock_get_token.called


@patch("app.search.ebay._get_access_token", return_value="dummy_token")
@patch(
    "app.search.ebay.get_requests",
    return_value={},
)
def test_search_ebay_items_no_data(mock_get_requests: AsyncMock, mock_get_token: AsyncMock) -> None:

    keywords = ["9999999999999"]
    option = {"search_type": 1, "search_result_limit": 10}

    results = ebay.search_ebay_items(keywords, option)

    assert isinstance(results, list)
    assert len(results) == 0
    assert mock_get_requests.called
    assert mock_get_token.called


@patch("app.search.ebay._get_access_token", return_value="dummy_token")
@patch("app.search.ebay.get_requests")
def test_search_ebay_items_raise_exception(
    mock_get_requests: AsyncMock, mock_get_token: AsyncMock
) -> None:
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = HTTPError("Unauthorized")
    mock_response.get.return_value = []
    mock_get_requests.return_value = mock_response

    keywords = ["9999999999999"]
    option = {"search_type": 1, "search_result_limit": 10}

    results = ebay.search_ebay_items(keywords, option)

    assert isinstance(results, list)
    assert len(results) == 0
    assert mock_get_requests.called
    assert mock_get_token.called
