# utils/formatter.py

import difflib
import re
from typing import Any, Optional

from app.models.enums import SearchType, Store
from app.models.product_data import ProductItem, WorkProductItem
from app.services.code_counter import ThreadSafeCodeCounter
from app.services.translator import translate_to_japanese

counter: ThreadSafeCodeCounter = ThreadSafeCodeCounter()


async def format(
    yahoo_items: list[dict[str, Any]],
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
        yahoo_items (list): Yahoo search results.
        rakuten_items (list): Rakuten search results.
        ebay_items (list): eBay search results.
        option (dict): Options for grouping.
    Returns:
        dict: Formatted product data.
    """

    # 商品データのグルーピング
    grouped_items: dict[str, WorkProductItem] = await _group_product_data(yahoo_items, {}, option, Store.YAHOO)
    grouped_items = await _group_product_data(rakuten_items, grouped_items, option, Store.RAKUTEN)
    grouped_items = await _group_product_data(ebay_items, grouped_items, option, Store.EBAY)

    # 商品データを整形して返す
    return _format_grouped_items(grouped_items)


async def _group_product_data(
    org_items: list[dict[str, Any]], grouped_items: dict[str, WorkProductItem], option: dict[str, Any], store: Store
) -> dict[str, WorkProductItem]:
    """
    Add product data to the grouped product data.

    Args:
        org_items (list): eBay search results.
        grouped_items (dict): Combined product data.
        option (dict): Options for grouping.
    Returns:
        dict: Combined product data.
    """

    if option["search_type"] == SearchType.JAN_CODE:
        # 商品の整形(JANコードあり)
        grouped_items = _group_by_jan_code(org_items, grouped_items, store)
    else:
        # 商品の整形(JANコードなし)
        grouped_items = await _group_by_product_name(org_items, grouped_items, store, option)

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

        # 存在しなければ新規作成
        if jan_code not in grouped_items:
            grouped_items[jan_code] = _create_initial_work_product_item()

        _update_item_in_grouped_items(grouped_items[jan_code], item, store)

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

    for item in (item for item in org_items):
        current_product_name_from_item = item.get("product_name", "")
        product_name_to_use_in_update = current_product_name_from_item

        # ebayの場合は商品名を日本語に変換
        if store == Store.EBAY:
            product_name_to_use_in_update = await translate_to_japanese(current_product_name_from_item)

        match_flg: bool = False
        for jan_code in list(grouped_items.keys()):
            yahoo_name = grouped_items[jan_code]["product_name"][Store.YAHOO.value]
            rakuten_name = grouped_items[jan_code]["product_name"][Store.RAKUTEN.value]
            ebay_name = grouped_items[jan_code]["product_name"][Store.EBAY.value]
            target_name = str(yahoo_name or rakuten_name or ebay_name)

            if _is_similarity(target_name, current_product_name_from_item, product_name_to_use_in_update, option):
                # 類似度が高い場合、同一商品とみなし既存の項目を更新
                _update_item_in_grouped_items(
                    grouped_items[jan_code],
                    item,
                    store,
                )
                match_flg = True
                break

        if not match_flg:
            # 1件もマッチしなかった場合は別途追加する
            code = str(item.get("jan_code") if item.get("jan_code") else "No-" + str(counter.get_next()))

            grouped_items[code] = _create_initial_work_product_item()
            _update_item_in_grouped_items(
                grouped_items[code],
                item,
                store,
            )

    return grouped_items


def _update_item_in_grouped_items(
    target_grouped_item: WorkProductItem,
    source_item_data: dict[str, Any],
    store: Store,
) -> None:
    """
    grouped_items内の既存または新規のWorkProductItemの情報を更新します。
    最安値のロジックを含みます。

    Args:
        target_grouped_item (WorkProductItem): 更新対象となるgrouped_items内のWorkProductItemオブジェクト。
        source_item_data (dict): 更新に使用する元のアイテムデータ（org_itemsの各item）。
        store_value (str): 現在処理しているストアの文字列値（"yahoo", "rakuten"など）。
        current_product_name (Optional[str]): _group_by_product_nameからの呼び出し時に、
                                                item.get("product_name")の代わりに設定したい商品名。
                                                Noneの場合はsource_item_dataから取得。
    """
    current_price_float = _get_safe_price(source_item_data.get("price"))
    target_grouped_item["work_price"][store.value].append(current_price_float)

    existing_target_price_for_store = target_grouped_item["target_price"][store.value]

    # 最安値の更新ロジック
    # current_price_float が有効な数値である場合に、target_priceと比較して更新
    if current_price_float is not None:
        if existing_target_price_for_store is None or current_price_float < existing_target_price_for_store:
            target_grouped_item["product_name"][store.value] = source_item_data.get("product_name")
            target_grouped_item["target_price"][store.value] = current_price_float
            target_grouped_item["url"][store.value] = source_item_data.get("url")
            target_grouped_item["image_url"][store.value] = source_item_data.get("image_url")


def _get_safe_price(raw_price):
    try:
        if raw_price is not None:
            return float(raw_price)
    except (ValueError, TypeError):
        pass
    return None


def _create_initial_work_product_item():
    return {
        "product_name": {"yahoo": None, "rakuten": None, "ebay": None},
        "work_price": {"yahoo": [], "rakuten": [], "ebay": []},
        "target_price": {"yahoo": None, "rakuten": None, "ebay": None},
        "url": {"yahoo": None, "rakuten": None, "ebay": None},
        "image_url": {"yahoo": None, "rakuten": None, "ebay": None},
    }


def _is_similarity(org_text: str, target_text1: str, target_text2: str, option: dict[str, Any]) -> bool:
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
        valid_yahoo_prices = [p for p in item["work_price"][Store.YAHOO.value] if p is not None]
        valid_rakuten_prices = [p for p in item["work_price"][Store.RAKUTEN.value] if p is not None]
        valid_ebay_prices = [p for p in item["work_price"][Store.EBAY.value] if p is not None]
        result.append(
            {
                "jan_code": None if jan_code.startswith("No-") else jan_code,
                "product_name": item["product_name"],
                "price": {
                    "yahoo": {
                        "min": min(valid_yahoo_prices) if valid_yahoo_prices else None,
                        "max": max(valid_yahoo_prices) if valid_yahoo_prices else None,
                        "target": item["target_price"][Store.YAHOO.value],
                    },
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
