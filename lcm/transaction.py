from dataclasses import dataclass

from .utils import is_sorted


@dataclass
class Transaction:
    items: list[int]

    def __post_init__(self):
        assert is_sorted(self.items), "Items must be in ascending order"

    def __eq__(self, other):
        return self.items == other.items
