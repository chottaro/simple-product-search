# search/ebay.py

import base64
import logging
import os
from typing import Any

import httpx
import requests
from app.models.enums import SearchType
from app.services.http_request import get_requests

EBAY_APP_ID = os.getenv("EBAY_APP_ID")
EBAY_CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def search_ebay_items(keywords: list[str], option: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Search eBay products.

    Args:
        keywords (list): Search keyword or jan codes.
        option (dict): Options for Searching.
    Returns:
        list: eBay product search results.
    """

    token: str = _get_access_token()
    if not token:
        logger.info("eBayトークン取得失敗")
        return []

    items: list[dict[str, Any]] = []
    async with httpx.AsyncClient() as client:
        search_url: str = "https://api.ebay.com/buy/browse/v1/item_summary/search"
        headers: dict[str, str] = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        search_params: dict[str, Any] = {"limit": option["search_result_limit"]}

        for keyword in keywords:
            try:
                search_params["q"] = keyword

                data: dict[str, Any] = await get_requests(search_url, headers, search_params)

                items.extend(parse_item(keyword, option["search_type"], data))
            except httpx.HTTPStatusError as e:
                logger.warning(f"eBay request failed for {keyword}: {e}")

    return items


def parse_item(keyword: str, search_type: SearchType, data: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        items: list[dict[str, Any]] = []
        for item in data.get("itemSummaries", []):
            items.append(
                {
                    "jan_code": keyword if search_type == SearchType.JAN_CODE else "",
                    "product_name": item.get("title"),
                    "price": float(item.get("price", {}).get("value", 0)),
                    "url": item.get("itemWebUrl"),
                    "image_url": item.get("image", {}).get("imageUrl"),
                }
            )
        return items
    except (KeyError, TypeError, ValueError) as e:
        logger.warning(f"Failed to parse item: {e}")
        return []


def _get_access_token() -> str:
    """
    Use the EBAY_APP_ID and EBAY_CLIENT_SECRET specified in .env to generate a token for use with the eBay API.

    Returns:
        Generated token.
    """
    credentials: str = f"{EBAY_APP_ID}:{EBAY_CLIENT_SECRET}"

    encoded_credentials: str = base64.b64encode(credentials.encode()).decode()

    headers: dict[str, str] = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}",
    }
    data: dict[str, str] = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope",
    }

    response: Any = requests.post("https://api.ebay.com/identity/v1/oauth2/token", headers=headers, data=data)

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        logger.info("Failed to get token:", response.text)
        return ""
