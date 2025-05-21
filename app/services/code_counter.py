import threading


class ThreadSafeCodeCounter:
    """
    A counter that is temporarily used when a code cannot be retrieved from a product search.
    """

    def __init__(self) -> None:
        """
        Initialize the counter.
        """

        self.value = 1
        self.lock = threading.Lock()

    def get_next(self) -> str:
        """
        Get incremented counters.

        Returns:
            str: 13 digit zero-padded value as in jan code.
        """

        with self.lock:
            current = self.value
            self.value += 1
            return str(current).zfill(13)

    def get_value(self) -> str:
        """
        Get the current count.

        Returns:
            str: Trhe current count.
        """

        with self.lock:
            return str(self.value).zfill(13)
