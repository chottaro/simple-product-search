from app.services.code_counter import ThreadSafeCodeCounter


def test_initial_value() -> None:
    counter = ThreadSafeCodeCounter()
    assert counter.get_next() == "0000000000001"
    assert counter.get_next() == "0000000000002"


def test_thread_safety() -> None:
    import threading

    counter = ThreadSafeCodeCounter()
    results = []

    def worker() -> None:
        results.append(counter.get_next())

    threads = [threading.Thread(target=worker) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(set(results)) == 100
    assert all(len(code) == 13 for code in results)


def test_get_value_returns_current() -> None:
    counter = ThreadSafeCodeCounter()
    counter.get_next()  # value becomes 2
    current_value = counter.get_value()
    assert current_value == "0000000000002"
