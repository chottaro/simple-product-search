# search/yahoo.py

import asyncio
import logging
import os
from typing import Any

import httpx
from app.models.enums import SearchType
from app.services.http_request import get_requests

YAHOO_APP_ID = os.getenv("YAHOO_APP_ID")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def search_yahoo_items_by_keyword(keyword: str, option: dict[str, Any]) -> list[dict[str, Any]]:
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
    option_for_keyword["search_type"] = SearchType.KEYWORD
    return await _search_yahoo_items([keyword], option_for_keyword)


async def search_yahoo_items_by_jan_code(jan_codes: list[str], option: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Search Yahoo products by JAN code.

    Args:
        jan_codes (list): JAN codes for searching.
        option (dict): Options for Searching.
    Returns:
        list: Yahoo product search results.
    """
    return await _search_yahoo_items(jan_codes, option)


async def _search_yahoo_items(keywords: list[str], option: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Search Yahoo products.

    Args:
        keywords (list): Search keyword or jan codes.
        option (dict): Options for Searching.
    Returns:
        list: Yahoo product search results.
    """

    items: list[dict[str, Any]] = []
    async with httpx.AsyncClient() as client:
        search_url: str = "https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch"
        search_params: dict[str, Any] = {
            "appid": YAHOO_APP_ID,
            "results": option["search_result_limit"],
            "in_stock": True,
        }

        for keyword in keywords:
            try:
                # 429のエラーを発生させないためにsleepを入れる(0.5だと429発生)
                await asyncio.sleep(0.6)

                if option["search_type"] == SearchType.JAN_CODE:
                    search_params["jan_code"] = keyword
                else:
                    search_params["query"] = keyword

                data: dict[str, Any] = await get_requests(search_url, params=search_params)

                items.extend(parse_item(data))
            except httpx.HTTPStatusError as e:
                logger.warning(f"Yahoo request failed for {keyword}: {e}")

    return items


def parse_item(data: dict[str, Any]) -> list[dict[str, Any]]:
    try:
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
    except (KeyError, TypeError, ValueError) as e:
        logger.warning(f"Failed to parse item: {e}")
        return []
