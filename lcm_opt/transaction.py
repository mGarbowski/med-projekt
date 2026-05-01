from typing import Self
from line_profiler import profile

class TransactionOpt:
    items: tuple[int, ...]
    offset: int
    weight: int
    interior_intersection: set[int]

    __slots__ = ("items", "offset", "weight", "interior_intersection")

    # @profile
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

    def __eq__(self, other):
        return self.items == other.items and self.offset == other.offset

    # @profile
    def item_position(self, item: int) -> int | None:
        # binary search is not better here
        try:
            return self.items.index(item, self.offset)
        except ValueError:
            return None

    # @profile
    def remove_infrequent_items(self, buckets: list[list[Self]], min_support: int):
        new_items = tuple(item for item in self.items if len(buckets[item]) >= min_support)
        self.items = new_items
        self.interior_intersection = set(new_items)
