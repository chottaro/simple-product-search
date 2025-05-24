# main.py

import asyncio
import logging
import sys

from dotenv import load_dotenv

from app.api import search_products
from app.models.product_data import ProductItem
from app.services.save import save_to_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def search(keyword: str) -> None:
    load_dotenv()

    search_type: int = 1
    translate_keyword: int = 1
    search_result_limit: int = 30
    similarity_threshold: float = 0.45

    try:
        formated_items: list[ProductItem] = await search_products(
            keyword, search_type, translate_keyword, search_result_limit, similarity_threshold
        )
        logger.info("Saving results ...")
        save_to_json(formated_items)

        logger.info("Done! Check output.json.")

    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    args = sys.argv
    print(args)
    if len(args) == 1:
        logger.info("The keyword is required.")
        sys.exit(1)

    asyncio.run(search(args[1]))
