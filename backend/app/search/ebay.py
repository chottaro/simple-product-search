# search/ebay.py

import base64
import logging
import os
from typing import Any

import requests
from app.services.http_request import get_requests

EBAY_APP_ID = os.getenv("EBAY_APP_ID")
EBAY_CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def search_ebay_items(keywords: list[str], option: dict[str, Any]) -> list[dict[str, Any]]:
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
    for keyword in keywords:
        item: list[dict[str, Any]] = _search_once(keyword, token, option)
        if not item:
            continue

        items.extend(item)

    return items


def _search_once(keyword: str, token: str, option: dict[str, Any]) -> list[dict[str, Any]]:
    """
    The number of product data items corresponding to search_result_limit is acquired.

    Args:
        keyword (str): Search keyword or jan code.
        token (str): Tokens required by ebay's API.
        option (dict): Options for Searching.
    Returns:
        list: eBay product search results.
    """

    search_url: str = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    search_params: dict[str, Any] = {"q": keyword, "limit": option["search_result_limit"]}
    data: dict[str, Any] = get_requests(search_url, headers, search_params)
    items: list[dict[str, Any]] = []
    for item in data.get("itemSummaries", []):
        items.append(
            {
                "jan_code": keyword if option["search_type"] == 1 else "",
                "product_name": item.get("title"),
                "price": float(item.get("price", {}).get("value", 0)),
                "url": item.get("itemWebUrl"),
                "image_url": item.get("image", {}).get("imageUrl"),
            }
        )

    return items


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
