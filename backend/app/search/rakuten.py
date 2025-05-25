# search/rakuten.py

import asyncio
import logging
import os
from typing import Any

import httpx
from app.models.enums import SearchType
from app.services.code_finder import find_jan_code
from app.services.http_request import get_requests

RAKUTEN_APP_ID = os.environ.get("RAKUTEN_APP_ID")

seen_jan_codes: set = set()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def search_rakuten_items(keywords: list[str], option: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Search Rakuten products.

    Args:
        keywords (list): Search keyword or jan codes.
        option (dict): Options for Searching.
    Returns:
        list: Rakuten product search results.
    """

    items: list[dict[str, Any]] = []
    async with httpx.AsyncClient() as client:
        search_url: str = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"
        search_params: dict[str, Any] = {
            "applicationId": RAKUTEN_APP_ID,
            "format": "json",
            "formatVersion": 2,
            "hits": option["search_result_limit"],
        }

        for keyword in keywords:
            try:
                # 429のエラーを発生させないためにsleepを入れる(0.2だと429発生)
                await asyncio.sleep(0.3)

                search_params["keyword"] = keyword

                data: dict[str, Any] = await get_requests(search_url, params=search_params)

                items.extend(parse_item(keyword, option["search_type"], data))
            except httpx.HTTPStatusError as e:
                logger.warning(f"Rakuten request failed for {keyword}: {e}")

    return items


def parse_item(keyword: str, search_type: SearchType, data: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        items: list[dict[str, Any]] = []
        for item in data.get("Items", []):
            jan_code_text_sources: list[str] = [
                item.get("itemName"),
                item.get("itemCaption"),
                item.get("itemUrl"),
            ]
            image_url = item.get("mediumImageUrls")[0] if len(item.get("mediumImageUrls")) > 0 else ""
            jan_code_text_sources.append(image_url)

            items.append(
                {
                    "jan_code": keyword if search_type == SearchType.JAN_CODE else find_jan_code(jan_code_text_sources),
                    "product_name": item.get("itemName"),
                    "price": item.get("itemPrice"),
                    "url": item.get("itemUrl"),
                    "image_url": image_url,
                }
            )
        return items
    except (KeyError, TypeError, ValueError) as e:
        logger.warning(f"Failed to parse item: {e}")
        return []
