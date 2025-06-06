import pytest
from app.models.enums import SearchType
from app.services import formatter


@pytest.mark.asyncio
async def test_format_with_jan_code() -> None:
    yahoo_items = [
        {
            "jan_code": "1234567890123",
            "product_name": "商品A-1",
            "price": 1000,
            "url": "https:/store.shopping.yahoo.co.jp/a",
            "image_url": "https://image.com/1.jpg",
        },
        {
            "jan_code": "1234567890123",
            "product_name": "商品A-2",
            "price": 800,
            "url": "https://store.shopping.yahoo.co.jp/b",
            "image_url": "https://image.com/2.jpg",
        },
    ]
    rakuten_items = [
        {
            "jan_code": "1234567890123",
            "product_name": "商品B-1",
            "price": 700,
            "url": "https://rakuten.com/a",
            "image_url": "https://image.com/3.jpg",
        },
        {
            "jan_code": "1234567890123",
            "product_name": "商品B-2",
            "price": 900,
            "url": "https://rakuten.com/b",
            "image_url": "https://image.com/4.jpg",
        },
    ]
    ebay_items = [
        {
            "jan_code": "1234567890123",
            "product_name": "Product C-1",
            "price": 12.12,
            "url": "https://ebay.com/a",
            "image_url": "https://image.com/5.jpg",
        },
        {
            "jan_code": "1234567890123",
            "product_name": "Product C-2",
            "price": 13.13,
            "url": "https://ebay.com/b",
            "image_url": "https://image.com/6.jpg",
        },
    ]
    option = {"search_type": SearchType.JAN_CODE}

    result = await formatter.format(yahoo_items, rakuten_items, ebay_items, option)

    assert len(result) == 1
    item = result[0]
    assert item["jan_code"] == "1234567890123"
    assert item["product_name"]["yahoo"] == "商品A-2"
    assert item["product_name"]["rakuten"] == "商品B-1"
    assert item["product_name"]["ebay"] == "Product C-1"
    assert item["price"]["yahoo"]["min"] == 800
    assert item["price"]["yahoo"]["max"] == 1000
    assert item["price"]["yahoo"]["target"] == 800
    assert item["price"]["rakuten"]["min"] == 700
    assert item["price"]["rakuten"]["max"] == 900
    assert item["price"]["rakuten"]["target"] == 700
    assert item["price"]["ebay"]["min"] == 12.12
    assert item["price"]["ebay"]["max"] == 13.13
    assert item["price"]["ebay"]["target"] == 12.12
    assert item["url"]["yahoo"] == "https://store.shopping.yahoo.co.jp/b"
    assert item["url"]["rakuten"] == "https://rakuten.com/a"
    assert item["url"]["ebay"] == "https://ebay.com/a"
    assert item["image_url"]["yahoo"] == "https://image.com/2.jpg"
    assert item["image_url"]["rakuten"] == "https://image.com/3.jpg"
    assert item["image_url"]["ebay"] == "https://image.com/5.jpg"


@pytest.mark.asyncio
async def test_format_with_product_name() -> None:
    yahoo_items = [
        {
            "jan_code": "",
            "product_name": "商品A-1",
            "price": 800,
            "url": "https://store.shopping.yahoo.co.jp/a",
            "image_url": "https://image.com/1.jpg",
        },
        {
            "jan_code": "",
            "product_name": "商品A-2",
            "price": 700,
            "url": "https://store.shopping.yahoo.co.jp/b",
            "image_url": "https://image.com/2.jpg",
        },
        {
            "jan_code": "9999999999999",
            "product_name": "テスト",
            "price": 700,
            "url": "https://store.shopping.yahoo.co.jp/c",
            "image_url": "https://image.com/3.jpg",
        },
    ]
    rakuten_items = [
        {
            "jan_code": "",
            "product_name": "商品A",
            "price": 1000,
            "url": "https://rakuten.com/a",
            "image_url": "https://image.com/4.jpg",
        },
        {
            "jan_code": "",
            "product_name": "商品A-2",
            "price": 900,
            "url": "https://rakuten.com/b",
            "image_url": "https://image.com/5.jpg",
        },
        {
            "jan_code": "9999999999999",
            "product_name": "テスト",
            "price": 800,
            "url": "https://rakuten.com/c",
            "image_url": "https://image.com/6.jpg",
        },
    ]
    ebay_items = [
        {
            "jan_code": "",
            "product_name": "Product A-1",
            "price": 12.12,
            "url": "https://ebay.com/a",
            "image_url": "https://image.com/7.jpg",
        },
        {
            "jan_code": "",
            "product_name": "Product A-2",
            "price": 13.13,
            "url": "https://ebay.com/b",
            "image_url": "https://image.com/8.jpg",
        },
        {
            "jan_code": "",
            "product_name": "other",
            "price": 14.14,
            "url": "https://ebay.com/c",
            "image_url": "https://image.com/9.jpg",
        },
    ]
    option = {"search_type": SearchType.KEYWORD}

    result = await formatter.format(yahoo_items, rakuten_items, ebay_items, option)

    assert len(result) == 3
    item = result[0]
    assert item["jan_code"] == None
    assert item["product_name"]["yahoo"] == "商品A-2"
    assert item["product_name"]["rakuten"] == "商品A-2"
    assert item["product_name"]["ebay"] == "Product A-1"
    assert item["price"]["yahoo"]["min"] == 700
    assert item["price"]["yahoo"]["max"] == 800
    assert item["price"]["yahoo"]["target"] == 700
    assert item["price"]["rakuten"]["min"] == 900
    assert item["price"]["rakuten"]["max"] == 1000
    assert item["price"]["rakuten"]["target"] == 900
    assert item["price"]["ebay"]["min"] == 12.12
    assert item["price"]["ebay"]["max"] == 13.13
    assert item["price"]["ebay"]["target"] == 12.12
    assert item["url"]["yahoo"] == "https://store.shopping.yahoo.co.jp/b"
    assert item["url"]["rakuten"] == "https://rakuten.com/b"
    assert item["url"]["ebay"] == "https://ebay.com/a"
    assert item["image_url"]["yahoo"] == "https://image.com/2.jpg"
    assert item["image_url"]["rakuten"] == "https://image.com/5.jpg"
    assert item["image_url"]["ebay"] == "https://image.com/7.jpg"

    item = result[1]
    assert item["jan_code"] == "9999999999999"
    assert item["product_name"]["yahoo"] == "テスト"
    assert item["product_name"]["rakuten"] == "テスト"
    assert item["product_name"]["ebay"] == None
    assert item["price"]["yahoo"]["min"] == 700
    assert item["price"]["yahoo"]["max"] == 700
    assert item["price"]["yahoo"]["target"] == 700
    assert item["price"]["rakuten"]["min"] == 800
    assert item["price"]["rakuten"]["max"] == 800
    assert item["price"]["rakuten"]["target"] == 800
    assert item["price"]["ebay"]["min"] == None
    assert item["price"]["ebay"]["max"] == None
    assert item["price"]["ebay"]["target"] == None
    assert item["url"]["yahoo"] == "https://store.shopping.yahoo.co.jp/c"
    assert item["url"]["rakuten"] == "https://rakuten.com/c"
    assert item["url"]["ebay"] == None
    assert item["image_url"]["yahoo"] == "https://image.com/3.jpg"
    assert item["image_url"]["rakuten"] == "https://image.com/6.jpg"
    assert item["image_url"]["ebay"] == None

    item = result[2]
    assert item["jan_code"] == None
    assert item["product_name"]["yahoo"] == None
    assert item["product_name"]["rakuten"] == None
    assert item["product_name"]["ebay"] == "other"
    assert item["price"]["yahoo"]["min"] == None
    assert item["price"]["yahoo"]["max"] == None
    assert item["price"]["yahoo"]["target"] == None
    assert item["price"]["rakuten"]["min"] == None
    assert item["price"]["rakuten"]["max"] == None
    assert item["price"]["rakuten"]["target"] == None
    assert item["price"]["ebay"]["min"] == 14.14
    assert item["price"]["ebay"]["max"] == 14.14
    assert item["price"]["ebay"]["target"] == 14.14
    assert item["url"]["yahoo"] == None
    assert item["url"]["rakuten"] == None
    assert item["url"]["ebay"] == "https://ebay.com/c"
    assert item["image_url"]["yahoo"] == None
    assert item["image_url"]["rakuten"] == None
    assert item["image_url"]["ebay"] == "https://image.com/9.jpg"
