def is_sorted(numbers: list[int]):
    for idx, number in enumerate(numbers[:-1]):
        if number > numbers[idx + 1]:
            return False

    return True
