def is_sorted(numbers: list[int]):
    for idx, number in enumerate(numbers[:-1]):
        if number > numbers[idx + 1]:
            return False

    return True


def contains_after(numbers: list[int], element: int, after_idx: int) -> bool:
    for i in range(after_idx + 1, len(numbers)):
        val = numbers[i]
        if val == element:
            return True
        if val > element:  # List is sorted
            return False
    return False
