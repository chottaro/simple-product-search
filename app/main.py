# main.py

import asyncio
import logging

from dotenv import load_dotenv

from app.api import search_products
from app.models.product_data import ProductItem

# from app.search.ebay import search_ebay_items
# from app.search.rakuten import search_rakuten_items
# from app.services.formatter import format
from app.services.save import save_to_json

# from typing import Any


# from app.services.translator import translate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    load_dotenv()

    keyword = "nintendo switch"
    search_type: int = 1
    translate_keyword: int = 1
    search_result_limit: int = 30
    similarity_threshold: float = 0.45

    formated_items: list[ProductItem] = await search_products(
        keyword, search_type, translate_keyword, search_result_limit, similarity_threshold
    )

    logger.info("Saving results ...")
    save_to_json(formated_items)

    logger.info("Done! Check output.json.")


if __name__ == "__main__":
    asyncio.run(main())
