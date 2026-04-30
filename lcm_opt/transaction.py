from typing import Self

from .utils import is_sorted


class TransactionOpt:
    items: list[int]
    offset: int
    weight: int
    interior_intersection: set[int]

    def __init__(
        self,
        items: list[int],
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

        assert is_sorted(self.items), "Items must be in ascending order"
        assert 0 <= self.offset < len(self.items), (
            "Offset must be a valid index in the items list"
        )

    @classmethod
    def with_offset(cls, transaction: Self, offset: int) -> Self:
        return cls(
            transaction.items,
            offset,
            transaction.weight,
            interior_intersection=set(transaction.interior_intersection),
        )

    def __eq__(self, other):
        return self.items == other.items and self.offset == other.offset

    def item_position(self, item: int) -> int | None:
        # TODO binary search
        try:
            return self.items.index(item, self.offset)
        except ValueError:
            return None

    def get_active_items_tuple(self) -> tuple[int, ...]:
        """Returns active part of the transaction as tuple (hashable)"""
        return tuple(self.items[self.offset :])

    def remove_infrequent_items(self, buckets: list[list[Self]], min_support: int):
        new_items = []
        for item in self.items:
            if len(buckets[item]) >= min_support:
                new_items.append(item)
        self.items = new_items
        self.interior_intersection = set(self.items)
