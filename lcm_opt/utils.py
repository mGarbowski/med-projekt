import bisect


def is_sorted(numbers: list[int]):
    for idx, number in enumerate(numbers[:-1]):
        if number > numbers[idx + 1]:
            return False

    return True


def contains_after(numbers: list[int], element: int, after_idx: int) -> bool:

    # binary search
    idx = bisect.bisect_left(numbers, element, lo=after_idx + 1)
    return idx != len(numbers) and numbers[idx] == element
