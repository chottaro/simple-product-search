import asyncio
import logging
import traceback
from typing import Any

from app.models.enums import Store
from app.models.product_data import ProductItem
from app.search.ebay import search_ebay_items
from app.search.rakuten import search_rakuten_items
from app.search.yahoo import (
    search_yahoo_items_by_jan_code,
    search_yahoo_items_by_keyword,
)
from app.services.formatter import format
from app.services.translator import translate
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/search")
async def search_products(
    keyword: str = Query(..., min_length=1),
    search_type: int = 1,
    translate_keyword: int = 1,
    search_result_limit: int = 30,
    similarity_threshold: float = 0.45,
) -> list[ProductItem]:
    """
    Search for products on Rakuten and eBay and return information grouped by JAN code or product name.
    Args:
        keyword (str): Keywords for searching products from Rakuten and eBay.
        search_type (int): Set the search method.

            1: Get JAN code by keyword search in Rakuten, and search Rakuten and eBay by JAN code.(Default)

            0: Search Rakuten and eBay by keyword.
        translate_keyword (int): Specifies whether to translate keywords.
            If you specify 1, rakuten searches in Japanese and ebay searches in English.

            0: Do not translate.

            1: Use translated keywords. (Default)

            2: Use both the original and translated words.
        search_result_limit (int): Number of items to be retrieved for each site. (This is not the number returned.)
        similarity_threshold (float):Similarity when translating and comparing product names retrieved from each site when search_type is 0.
            The default is 0.45.
    Returns:
        list: Product information on each site.
        Rakuten has priority for image_url.
    """

    if not keyword.strip():
        raise HTTPException(status_code=400, detail="The keyword is required.")

    option: dict[str, Any] = {
        "search_type": search_type,
        "translate_keyword": translate_keyword,
        "search_result_limit": search_result_limit,
        "similarity_threshold": similarity_threshold,
    }

    translated: dict[str, str] = await translate(keyword)
    keyword_en: str = translated["en"]
    keyword_ja: str = translated["ja"]
    combined_keyword: str = f"{keyword_en} {keyword_ja}"

    search_keyword: str = keyword
    if translate_keyword == 1:
        search_keyword = keyword_ja
    elif translate_keyword == 2:
        search_keyword = combined_keyword

    logger.info("Retrieving Yahoo products by keyword ...")
    logger.info(f"keyword: {search_keyword}")
    yahoo_items: list[dict[str, Any]] = await search_yahoo_items_by_keyword(search_keyword, option)
    logger.info(f"Number of items: {len(yahoo_items)}")

    jan_codes: list[str] = list(set([item["jan_code"] for item in yahoo_items if item.get("jan_code")]))
    logger.info(f"Jan codes:{jan_codes}")

    keyword_map = get_keyword_map(keyword, keyword_en, keyword_ja, combined_keyword, jan_codes)

    async def get_async_items():
        tasks = [
            search_items(keyword_map, option, Store.YAHOO),
            search_items(keyword_map, option, Store.RAKUTEN),
            search_items(keyword_map, option, Store.EBAY),
        ]
        yahoo_items, rakuten_items, ebay_items = await asyncio.gather(*tasks)
        return yahoo_items, rakuten_items, ebay_items

    yahoo_items, rakuten_items, ebay_items = await get_async_items()

    logger.info("Formatting product data ...")
    formated_items: list[ProductItem] = await format(yahoo_items, rakuten_items, ebay_items, option)
    logger.info(f"Number of formatted items: {len(formated_items)}")

    return formated_items


async def search_items(keyword_map, option, store: Store) -> list[dict[str, Any]]:
    logger.info(f"Retrieving {store.value} products ...")
    keywords: list[str] = keyword_map[store][option["search_type"]][option["translate_keyword"]]
    items: list[dict[str, Any]] = []
    if store == Store.YAHOO:
        items = await search_yahoo_items_by_jan_code(keywords, option)
    elif store == Store.RAKUTEN:
        items = await search_rakuten_items(keywords, option)
    elif store == Store.EBAY:
        items = await search_ebay_items(keywords, option)
    logger.info(f"Number of items in {store.value}: {len(items)}")

    return items


def get_keyword_map(
    keyword, keyword_en, keyword_ja, combined_keyword, jan_codes
) -> dict[Store, dict[int, dict[int, Any]]]:
    """
    Define keyword mappings for each platform, search type, and translation option.
    Args:
        keyword (str): The original keyword.
        keyword_en (str): Keywords translated into Japanese.
        keyword_ja (str): Keywords translated into English.
        combined_keyword (str): Japanese and English keywords.
        jan_codes (Store): JAN codes.
    Returns:
        dict: Mapped Keywords.
    """
    keyword_map = {
        Store.YAHOO: {
            0: {
                0: [keyword],
                1: [keyword_ja],
                2: [combined_keyword],
            },
            1: {
                0: jan_codes,
                1: jan_codes,
                2: jan_codes,
            },
        },
        Store.RAKUTEN: {
            0: {
                0: [keyword],
                1: [keyword_ja],
                2: [combined_keyword],
            },
            1: {
                0: jan_codes,
                1: jan_codes,
                2: jan_codes,
            },
        },
        Store.EBAY: {
            0: {
                0: [keyword],
                1: [keyword_en],
                2: [combined_keyword],
            },
            1: {
                0: jan_codes,
                1: jan_codes,
                2: jan_codes,
            },
        },
    }

    return keyword_map


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "An error occurred inside the server."},
    )
