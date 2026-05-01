from typing import TextIO, Self
from line_profiler import profile

from .transaction import TransactionOpt


class DatasetOpt:
    def __init__(self, transactions: list[TransactionOpt]):
        self.transactions = transactions
        self.max_item = self._get_max_item_from_transactions(transactions)
        self.unique_items = self._get_unique_items_from_transactions(transactions)

    @staticmethod
    @profile
    def _get_unique_items_from_transactions(
        transactions: list[TransactionOpt],
    ) -> set[int]:
        unique_items = set()
        for transaction in transactions:
            unique_items.update(transaction.items)
        return unique_items

    @staticmethod
    def _get_max_item_from_transactions(transactions: list[TransactionOpt]) -> int:
        """Get the maximum item ID from a list of transactions.

        Transaction items are sorted
        """
        return max((t.items[-1] for t in transactions if t.items), default=0)

    @classmethod
    # @profile
    def from_stream(cls, io: TextIO) -> Self:
        transactions = [
            TransactionOpt(items=tuple(map(int, line.split())))
            for line in io
        ]
        return cls(transactions)

    @classmethod
    def from_lists(cls, item_lists: list[tuple[int, ...]]) -> Self:
        return cls([TransactionOpt(items) for items in item_lists])
