# # utils/http_request.py

from typing import Any

import requests


def get_requests(url: str, headers: dict[str, str] = {}, params: dict[str, Any] = {}) -> Any:
    """
    Send a GET request with the specified URL and parameters.

    Args:
        url (str): URL.
        headers (dict): Header information for GET requests.
        params (dict): Parameters used in GET requests.
    Returns:
        any: HTTP response in JSON format.
    """

    response: Any = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()
