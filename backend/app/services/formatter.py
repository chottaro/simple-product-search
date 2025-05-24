# utils/formatter.py

import difflib
import re
from typing import Any

from app.models.enums import Store
from app.models.product_data import ProductItem, WorkProductItem
from app.services.code_counter import ThreadSafeCodeCounter
from app.services.translator import translate_to_japanese

counter: ThreadSafeCodeCounter = ThreadSafeCodeCounter()


async def format(
    rakuten_items: list[dict[str, Any]],
    ebay_items: list[dict[str, Any]],
    option: dict[str, Any],
) -> list[ProductItem]:
    """
    combines the product data of Rakuten and eBay and forms the data.
    The data join conditions are as follows:
    Rakuten:
    ・With JAN code ... Collecting data by JAN code
    ・No JAN code ... Compare trade names, compare similarity with similarity_threshold, and summarize the closest ones
    eBay:
    ・search_type is 1... Collects data with JAN code
    ・search_type is other than 1 ... Translate according to the comparison target (Rakuten or eBay), compare similarity by similarity_threshold, and summarize the closest ones.

    Args:
        rakuten_items (list): Rakuten search results.
        ebay_items (list): eBay search results.
        option (dict): Options for grouping.
    Returns:
        dict: Formatted product data.
    """

    # 商品データのグルーピング
    grouped_items: dict[str, WorkProductItem] = await _group_rakuten_product_data(
        rakuten_items, option
    )
    grouped_items = await _group_ebay_product_data(ebay_items, grouped_items, option)

    # 商品データを整形して返す
    return _format_grouped_items(grouped_items)


async def _group_rakuten_product_data(
    org_items: list[dict[str, Any]], option: dict[str, Any]
) -> dict[str, WorkProductItem]:
    """
    Group Rakuten product data.

    Args:
        org_items (list): Rakuten search results.
        option (dict): Options for grouping.
    Returns:
        dict: The combined Rakuten product data.
    """

    grouped_items: dict[str, WorkProductItem] = {}

    # 楽天商品の整形(JANコードあり)
    grouped_items = _group_by_jan_code(org_items, grouped_items, Store.RAKUTEN)

    # 楽天商品の整形(JANコードなし)
    grouped_items = await _group_by_product_name(org_items, grouped_items, Store.RAKUTEN, option)

    return grouped_items


async def _group_ebay_product_data(
    org_items: list[dict[str, Any]],
    grouped_items: dict[str, WorkProductItem],
    option: dict[str, Any],
) -> dict[str, WorkProductItem]:
    """
    Add eBay product data to the grouped product data.

    Args:
        org_items (list): eBay search results.
        grouped_items (dict): Combined product data.
        option (dict): Options for grouping.
    Returns:
        dict: Combined Rakuten and eBay product data.
    """

    if option["search_type"] == 1:
        # ebay商品の整形(JANコードあり)
        grouped_items = _group_by_jan_code(org_items, grouped_items, Store.EBAY)
    else:
        # ebay商品の整形(JANコードなし)
        grouped_items = await _group_by_product_name(org_items, grouped_items, Store.EBAY, option)

    return grouped_items


def _group_by_jan_code(
    org_items: list[dict[str, Any]], grouped_items: dict[str, WorkProductItem], store: Store
) -> dict[str, WorkProductItem]:
    """
    Group product data by JAN code.

    Args:
        org_items (list): Product data to group.
        grouped_items (dict): Combined product data.
        store (Store): Enumerated stores.
    Returns:
        dict: Result of grouping org_items into grouped_items.
    """

    for item in (item for item in org_items if item.get("jan_code")):
        jan_code = item["jan_code"]
        if jan_code in grouped_items:
            grouped_items[jan_code]["work_price"][store.value].append(item.get("price"))
            if not grouped_items[jan_code]["product_name"][store.value]:
                grouped_items[jan_code]["product_name"][store.value] = item.get("product_name")
                grouped_items[jan_code]["target_price"][store.value] = item.get("price")
                grouped_items[jan_code]["url"][store.value] = item.get("url")
                grouped_items[jan_code]["image_url"][store.value] = item.get("image_url")

        else:
            grouped_items[jan_code] = {
                "product_name": {
                    "rakuten": item.get("product_name") if store == Store.RAKUTEN else None,
                    "ebay": item.get("product_name") if store == Store.EBAY else None,
                },
                "work_price": {
                    "rakuten": [item.get("price")] if store == Store.RAKUTEN else [],
                    "ebay": [item.get("price")] if store == Store.EBAY else [],
                },
                "target_price": {
                    "rakuten": item.get("price") if store == Store.RAKUTEN else None,
                    "ebay": item.get("price") if store == Store.EBAY else None,
                },
                "url": {
                    "rakuten": item.get("url") if store == Store.RAKUTEN else None,
                    "ebay": item.get("url") if store == Store.EBAY else None,
                },
                "image_url": {
                    "rakuten": item.get("image_url") if store == Store.RAKUTEN else None,
                    "ebay": item.get("image_url") if store == Store.EBAY else None,
                }
            }

    return grouped_items


async def _group_by_product_name(
    org_items: list[dict[str, Any]],
    grouped_items: dict[str, WorkProductItem],
    store: Store,
    option: dict[str, Any],
) -> dict[str, WorkProductItem]:
    """
    Group product data by product name.

    Args:
        org_items (list): Product data to group.
        grouped_items (dict): Combined product data.
        store (Store): Enumerated stores.
        option (dict): Options for grouping.
    Returns:
        dict: Result of grouping org_items into grouped_items.
    """

    for item in (item for item in org_items if not item.get("jan_code")):
        current_product_name = item.get("product_name", "")
        translate_product_name = current_product_name

        # ebayの場合は商品名を日本語に変換
        if store == Store.EBAY:
            translate_product_name = await translate_to_japanese(current_product_name)

        for jan_code in grouped_items:
            rakuten_name = grouped_items[jan_code]["product_name"][Store.RAKUTEN.value]
            ebay_name = grouped_items[jan_code]["product_name"][Store.EBAY.value]
            target_name = str(rakuten_name or ebay_name)

            match_flg: bool = False
            if _is_similarity(target_name, current_product_name, translate_product_name, option):
                # ファイル名の類似度が規定値を超えた場合は同一商品とみなす
                grouped_items[jan_code]["work_price"][store.value].append(item.get("price"))
                if not grouped_items[jan_code]["product_name"][store.value]:
                    grouped_items[jan_code]["product_name"][store.value] = current_product_name
                    grouped_items[jan_code]["target_price"][store.value] = item.get("price")
                    grouped_items[jan_code]["url"][store.value] = item.get("url")
                    grouped_items[jan_code]["image_url"][store.value] = item.get("image_url")

                match_flg = True
                break

        if not match_flg:
            # 1件もマッチしなかった場合は別途追加する
            code: str = "No-" + counter.get_next()
            grouped_items[code] = {
                "product_name": {
                    "rakuten": item.get("product_name") if store == Store.RAKUTEN else None,
                    "ebay": item.get("product_name") if store == Store.EBAY else None,
                },
                "work_price": {
                    "rakuten": [item.get("price")] if store == Store.RAKUTEN else [],
                    "ebay": [item.get("price")] if store == Store.EBAY else [],
                },
                "target_price": {
                    "rakuten": item.get("price") if store == Store.RAKUTEN else None,
                    "ebay": item.get("price") if store == Store.EBAY else None,
                },
                "url": {
                    "rakuten": item.get("url") if store == Store.RAKUTEN else None,
                    "ebay": item.get("url") if store == Store.EBAY else None,
                },
                "image_url": {
                    "rakuten": item.get("image_url") if store == Store.RAKUTEN else None,
                    "ebay": item.get("image_url") if store == Store.EBAY else None,
                },
            }

    return grouped_items


def _is_similarity(
    org_text: str, target_text1: str, target_text2: str, option: dict[str, Any]
) -> bool:
    """
    Check if the specified trade names are similar.

    Args:
        org_text (str): The name of the product to be compared.
        target_text1 (str): The product name to compare.
        target_text2 (str): The translated product name to compare.
        option (dict): Options for grouping.
    Returns:
        bool: True if the approximation exceeds the threshold, False otherwise.
    """

    norm_org = _normalize_text(org_text)
    candidates = {_normalize_text(target_text1), _normalize_text(target_text2)}
    threshold = option.get("similarity_threshold", 0.5)
    return any(difflib.SequenceMatcher(None, norm_org, t).ratio() >= threshold for t in candidates)


def _normalize_text(text: str) -> str:
    """
    Normalize trade names for easier comparison.

    Args:
        text (str): Character string to be normalized.
    Returns:
        str: Normalized string.
    """

    text = text.lower()
    text = re.sub(r"[【】「」『』()]", "", text)
    text = re.sub(r"[-/]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _format_grouped_items(grouped_items: dict[str, WorkProductItem]) -> list[ProductItem]:
    """
    Format grouped commodity data.

    Args:
        grouped_items (dict): Combined product data.
    Returns:
        list: Formatted product data.
    """
    result: list[ProductItem] = []
    for jan_code, item in grouped_items.items():
        valid_rakuten_prices = [p for p in item["work_price"][Store.RAKUTEN.value] if p is not None]
        valid_ebay_prices = [p for p in item["work_price"][Store.EBAY.value] if p is not None]
        result.append(
            {
                "jan_code": None if jan_code.startswith("No-") else jan_code,
                "product_name": item["product_name"],
                "price": {
                    "rakuten": {
                        "min": min(valid_rakuten_prices) if valid_rakuten_prices else None,
                        "max": max(valid_rakuten_prices) if valid_rakuten_prices else None,
                        "target": item["target_price"][Store.RAKUTEN.value],
                    },
                    "ebay": {
                        "min": min(valid_ebay_prices) if valid_ebay_prices else None,
                        "max": max(valid_ebay_prices) if valid_ebay_prices else None,
                        "target": item["target_price"][Store.EBAY.value],
                    },
                },
                "url": item["url"],
                "image_url": item["image_url"],
            }
        )

    return result
