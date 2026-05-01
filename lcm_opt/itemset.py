from dataclasses import dataclass

from base.abstract_itemset import AbstractItemset


@dataclass
class ItemsetOpt(AbstractItemset):
    items: list[int]
    support: int

    __slots__ = ('items', 'support')

    def to_spmf_line(self) -> str:
        return f"{' '.join(str(item) for item in self.items)} #SUP: {self.support}"
