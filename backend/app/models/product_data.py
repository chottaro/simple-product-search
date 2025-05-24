# common/product_data.py

from typing_extensions import Any, Literal, Optional, TypedDict


class PriceInfo(TypedDict, total=False):
    min: Optional[float]
    max: Optional[float]
    target: Optional[float]


class UrlInfo(TypedDict):
    rakuten: Optional[str]
    ebay: Optional[str]


class ProductNameInfo(TypedDict):
    rakuten: Optional[str]
    ebay: Optional[str]

class ImageUrlInfo(TypedDict):
    rakuten: Optional[str]
    ebay: Optional[str]

class WorkPrice(TypedDict):
    rakuten: list[Optional[float]]
    ebay: list[Optional[float]]

class TargetPrice(TypedDict):
    rakuten: Optional[float]
    ebay: Optional[float]

class WorkProductItem(TypedDict):
    product_name: ProductNameInfo
    work_price: WorkPrice
    target_price: TargetPrice
    url: UrlInfo
    image_url: ImageUrlInfo


class ProductItem(TypedDict):
    jan_code: Optional[str]
    product_name: ProductNameInfo
    price: dict[Literal["rakuten", "ebay"], PriceInfo]
    url: UrlInfo
    image_url: ImageUrlInfo
