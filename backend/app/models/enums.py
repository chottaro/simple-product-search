# common/enums.py

from enum import Enum


class Store(Enum):
    """
    An Enum that defines the stores for which the corresponding products are searched.
    """

    EBAY = "ebay"
    RAKUTEN = "rakuten"
    YAHOO = "yahoo"
