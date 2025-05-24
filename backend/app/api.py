import logging
import traceback
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.models.product_data import ProductItem
from app.search.ebay import search_ebay_items
from app.search.rakuten import search_rakuten_items
from app.services.formatter import format
from app.services.translator import translate

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

     .. code-block:: json

    [
        {
            "jan_code": "4902370548495",
            "product_name": {
            "rakuten": "任天堂｜Nintendo Nintendo Switch（有機ELモデル）",
            "ebay": "Nintendo Switch White Edition"
            },
            "price": {
            "rakuten": {
                "min": 37978,
                "max": 46500
            },
            "ebay": {
                "min": 94.99,
                "max": 600
            }
            },
            "url": {
            "rakuten": "https://item.rakuten.co.jp/example",
            "ebay": "https://www.ebay.com/example"
            },
            "image_url": "https://thumbnail.image.rakuten.co.jp/example.jpg"
        },
        :
    ]

    Args:
        keyword (str): Keywords for searching products from Rakuten and eBay.
        search_type (int): Set the search method.

            1: Get JAN code by keyword search in Rakuten, and search Rakuten and eBay by JAN code.(Default)

            0: Search Rakuten and eBay by keyword.
        translate_keyword (int): Specifies whether to perform translation if search_type is 0.
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

    rakuten_keyword: str = keyword
    if translate_keyword == 1:
        rakuten_keyword = keyword_ja
    elif translate_keyword == 2:
        rakuten_keyword = combined_keyword

    logger.info("Retrieving Rakuten products by keyword search ...")
    logger.info(f"keyword: {rakuten_keyword}")
    rakuten_items: list[dict[str, Any]] = search_rakuten_items([rakuten_keyword], option)
    logger.info(f"Number of items: {len(rakuten_items)}")

    if search_type == 1:
        logger.info("Search by JAN code from Rakuten search results ...")
        jan_codes: list[str] = list(set([item["jan_code"] for item in rakuten_items]))
        logger.info(f"Jan codes:{jan_codes}")
        # Janコードで再度検索
        rakuten_items = search_rakuten_items(jan_codes, option)
        logger.info(f"Number of items: {len(rakuten_items)}")

    ebay_keywords: list[str] = [keyword]
    if search_type == 1:
        ebay_keywords = jan_codes
    else:
        if translate_keyword == 1:
            ebay_keywords = [keyword_en]
        elif translate_keyword == 2:
            ebay_keywords = [combined_keyword]

    logger.info("Retrieving eBay items ...")
    logger.info(f"keyword: {ebay_keywords}")
    ebay_items: list[dict[str, Any]] = search_ebay_items(ebay_keywords, option)
    logger.info(f"Number of items: {len(ebay_items)}")

    logger.info("Formatting product data ...")
    formated_items: list[ProductItem] = await format(rakuten_items, ebay_items, option)
    logger.info(f"Number of formatted items: {len(formated_items)}")

    return formated_items


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "An error occurred inside the server."},
    )
