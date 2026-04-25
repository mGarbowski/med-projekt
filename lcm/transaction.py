from typing import Self

from .utils import is_sorted


class Transaction:
    items: list[int]
    offset: int
    original_transaction: Self

    def __init__(
        self, items: list[int], offset: int = 0, original_transaction: Self = None
    ):
        self.items = items
        self.offset = offset
        self.original_transaction = (
            original_transaction if original_transaction is not None else self
        )

        assert is_sorted(self.items), "Items must be in ascending order"
        assert 0 <= self.offset < len(self.items), (
            "Offset must be a valid index in the items list"
        )

    @classmethod
    def with_offset(cls, transaction: Self, offset: int) -> Self:
        return cls(transaction.items, offset, transaction.original_transaction)

    def __eq__(self, other):
        return self.items == other.items and self.offset == other.offset

    def item_position(self, item: int) -> int | None:
        # TODO binary search
        try:
            return self.items.index(item, self.offset)
        except ValueError:
            return None

    def remove_infrequent_items(
        self, buckets: tuple[list[Self], ...], min_support: int
    ):
        new_items = []
        for item in self.items:
            if len(buckets[item]) >= min_support:
                new_items.append(item)
        self.items = new_items
