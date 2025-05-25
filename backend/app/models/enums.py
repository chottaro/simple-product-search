# common/enums.py

from enum import Enum


class SearchType(Enum):
    """
    An enum that defines how to search for products.
    """

    KEYWORD = "0"
    JAN_CODE = "1"


class TranslateKeyword(Enum):
    """
    An enum that keywords used in the search.
    """

    ORIGINAL = "0"
    TRANSLATE = "1"
    ORIGINAL_AND_TRANSLATE = "2"


class Store(Enum):
    """
    An Enum that defines the stores for which the corresponding products are searched.
    """

    EBAY = "ebay"
    RAKUTEN = "rakuten"
    YAHOO = "yahoo"
