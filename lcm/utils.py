def is_sorted(numbers: list[int]):
    for idx, number in enumerate(numbers[:-1]):
        if number > numbers[idx + 1]:
            return False

    return True


def contains_after(numbers: list[int], element: int, after_idx: int) -> bool:
    # TODO binary search
    return element in numbers[after_idx + 1 :]
