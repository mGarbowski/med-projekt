from dataclasses import dataclass
from typing import Self

from .utils import is_sorted


@dataclass
class Transaction:
    items: list[int]

    def __post_init__(self):
        assert is_sorted(self.items), "Items must be in ascending order"

    def __eq__(self, other):
        return self.items == other.items

    def remove_infrequent_items(
        self, buckets: tuple[list[Self], ...], min_support: int
    ):
        new_items = []
        for item in self.items:
            if len(buckets[item]) >= min_support:
                new_items.append(item)
        self.items = new_items
