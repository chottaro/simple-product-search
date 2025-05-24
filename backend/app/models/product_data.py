# common/product_data.py

from typing_extensions import Any, Literal, Optional, TypedDict


class PriceInfo(TypedDict, total=False):
    min: Optional[float]
    max: Optional[float]
    target: Optional[float]


class UrlInfo(TypedDict):
    yahoo: Optional[str]
    rakuten: Optional[str]
    ebay: Optional[str]


class ProductNameInfo(TypedDict):
    yahoo: Optional[str]
    rakuten: Optional[str]
    ebay: Optional[str]


class ImageUrlInfo(TypedDict):
    yahoo: Optional[str]
    rakuten: Optional[str]
    ebay: Optional[str]


class WorkPrice(TypedDict):
    yahoo: list[Optional[float]]
    rakuten: list[Optional[float]]
    ebay: list[Optional[float]]


class TargetPrice(TypedDict):
    yahoo: Optional[float]
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
    price: dict[Literal["yahoo", "rakuten", "ebay"], PriceInfo]
    url: UrlInfo
    image_url: ImageUrlInfo
