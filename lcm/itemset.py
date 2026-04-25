from dataclasses import dataclass

from .utils import is_sorted


@dataclass
class Itemset:
    items: list[int]
    support: int

    def __post_init__(self):
        assert is_sorted(self.items), "Items must be in ascending order"

    def to_spmf_line(self) -> str:
        return f"{' '.join(str(item) for item in self.items)} #SUP: {self.support}"
