import bisect
from typing import Self


class TransactionOpt:
    items: tuple[int, ...]
    offset: int
    weight: int
    interior_intersection: set[int]

    def __init__(
        self,
        items: tuple[int, ...],
        offset: int = 0,
        weight: int = 1,
        interior_intersection: set[int] | None = None,
    ):
        self.items = items
        self.offset = offset
        self.weight = weight

        if interior_intersection is None:
            self.interior_intersection = set(items)
        else:
            self.interior_intersection = interior_intersection

        assert 0 <= self.offset < len(self.items), (
            "Offset must be a valid index in the items list"
        )

    __slots__ = ("items", "offset", "weight", "interior_intersection")

    def __eq__(self, other):
        return self.items == other.items and self.offset == other.offset

    def item_position(self, item: int) -> int | None:
        # binary search
        idx = bisect.bisect_left(self.items, item, lo=self.offset)
        if idx != len(self.items) and self.items[idx] == item:
            return idx

        return None

    def remove_infrequent_items(self, buckets: list[list[Self]], min_support: int):
        new_items = []
        for item in self.items:
            if len(buckets[item]) >= min_support:
                new_items.append(item)
        self.items = tuple(new_items)
        self.interior_intersection = set(self.items)
