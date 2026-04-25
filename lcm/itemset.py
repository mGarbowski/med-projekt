from dataclasses import dataclass

from .utils import is_sorted


@dataclass
class Itemset:
    items: list[int]
    support: int

    def __post_init__(self):
        assert is_sorted(self.items), "Items must be in ascending order"
