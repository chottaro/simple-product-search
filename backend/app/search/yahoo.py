# search/yahoo.py

import logging
import os
import time
from typing import Any

from app.services.http_request import get_requests

YAHOO_APP_ID = os.getenv("YAHOO_APP_ID")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def search_yahoo_items_by_keyword(keyword: str, option: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Search Yahoo products by keyword.

    Args:
        keywords (str): Keyword for searching.
        option (dict): Options for Searching.
    Returns:
        list: Yahoo product search results.
    """

    # 強制的にキーワード検索を行う
    option_for_keyword = option.copy()
    option_for_keyword["search_type"] = 0
    return _search_yahoo_items([keyword], option_for_keyword)


def search_yahoo_items_by_jan_code(jan_codes: list[str], option: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Search Yahoo products by JAN code.

    Args:
        jan_codes (list): JAN codes for searching.
        option (dict): Options for Searching.
    Returns:
        list: Yahoo product search results.
    """
    return _search_yahoo_items(jan_codes, option)


def _search_yahoo_items(keywords: list[str], option: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Search Yahoo products.

    Args:
        keywords (list): Search keyword or jan codes.
        option (dict): Options for Searching.
    Returns:
        list: Yahoo product search results.
    """

    items: list[dict[str, Any]] = []
    for keyword in keywords:
        # 429のエラーを発生させないためにsleepを入れる(0.4だと429発生)
        time.sleep(0.5)

        item: list[dict[str, Any]] = _search_once(keyword, option)
        if not item:
            continue

        items.extend(item)

    return items


def _search_once(keyword: str, option: dict[str, Any]) -> list[dict[str, Any]]:
    """
    The number of product data items corresponding to search_result_limit is acquired.

    Args:
        keyword (str): Search keyword or jan code.
        token (str): Tokens required by Yahoo's API.
        option (dict): Options for Searching.
    Returns:
        list: Yahoo product search results.
    """

    search_url: str = "https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch"
    search_params: dict[str, Any] = {
        "appid": YAHOO_APP_ID,
        "results": option["search_result_limit"],
    }
    if option["search_type"] == 1:
        search_params["jan_code"] = keyword
    else:
        search_params["query"] = keyword

    data: dict[str, Any] = get_requests(search_url, params=search_params)
    items: list[dict[str, Any]] = []
    for item in data.get("hits", []):
        items.append(
            {
                "jan_code": item.get("janCode"),
                "product_name": item.get("name"),
                "price": float(item.get("price")),
                "url": item.get("url"),
                "image_url": item.get("image", {}).get("medium"),
            }
        )

    return items
