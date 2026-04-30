from lcm.utils import is_sorted


def test_is_sorted():
    assert is_sorted([1, 3, 4, 6])
    assert not is_sorted([1, 2, 7, 4, 5])
