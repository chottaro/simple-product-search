# search/rakuten.py

import logging
import os
import time
from typing import Any

from app.services.code_finder import find_jan_code
from app.services.http_request import get_requests

RAKUTEN_APP_ID = os.environ.get("RAKUTEN_APP_ID")

seen_jan_codes: set = set()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def search_rakuten_items(keywords: list[str], option: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Search Rakuten products.

    Args:
        keywords (list): Search keyword or jan codes.
        option (dict): Options for Searching.
    Returns:
        list: Rakuten product search results.
    """

    all_items: list[dict[str, Any]] = []
    for keyword in keywords:
        keyword_items: list[dict[str, Any]] = []
        option["page"] = 1
        while True:
            # 429のエラーを発生させないためにsleepを入れる(0.2だと429発生)
            time.sleep(0.3)

            items: list[dict[str, Any]] = _search_once(keyword, option)
            if len(items) == 0 or option["page"] >= 100:
                # データが取得できなかった時点で処理終了
                break

            keyword_items.extend(items)

            if option["search_type"] == 1:
                # コード検索の場合はページ単位で検索しないため処理終了
                break

            if len(keyword_items) >= option["search_result_limit"]:
                # キーワードごとに想定件数分を取得
                keyword_items = keyword_items[0 : option["search_result_limit"]]
                break

        all_items.extend(keyword_items)

    return all_items


def _search_once(keyword: str, option: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Search according to "search_type".
    When search_type is 1, the number of product data items corresponding to search_result_limit is acquired.
    When search_type is other than 1, the number of pages specified in option is acquired.

    Args:
        keyword (str): Search keyword or jan code.
        option (list): Options for Searching.
    Returns:
        list: Rakuten product search results.
    """

    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"
    params: dict[str, Any] = {
        "applicationId": RAKUTEN_APP_ID,
        "format": "json",
        "keyword": keyword,
        "formatVersion": 2,
    }
    if option["search_type"] == 1:
        # コード検索の場合は指定件数分取得
        params["hits"] = option["search_result_limit"]
    else:
        # キーワード検索の場合は指定件数未満の場合が発生するのでページ単位で取得
        params["page"] = option.get("page")

    data: dict[str, Any] = get_requests(url, params=params)

    items: list[dict[str, Any]] = []
    for item in data.get("Items", []):
        jan_code_text_sources: list[str] = [
            item.get("itemName"),
            item.get("itemCaption"),
            item.get("itemUrl"),
        ]
        image_url = item.get("mediumImageUrls")[0] if len(item.get("mediumImageUrls")) > 0 else ""
        jan_code_text_sources.append(image_url)

        jan_code: str = find_jan_code(jan_code_text_sources)

        if option.get("search_type") == 1 and jan_code == "":
            # コード検索の場合はコードが取得できなかったデータはスキップ
            continue

        items.append(
            {
                "jan_code": jan_code,
                "product_name": item.get("itemName"),
                "price": item.get("itemPrice"),
                "url": item.get("itemUrl"),
                "image_url": image_url,
            }
        )

    # 次の検索のためにページをインクリメント
    option["page"] += 1

    return items
