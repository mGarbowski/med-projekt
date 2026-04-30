from typing import TextIO, Self

from .transaction import TransactionOpt


class DatasetOpt:
    def __init__(self, transactions: list[TransactionOpt]):
        self.transactions = transactions
        self.max_item = self._get_max_item_from_transactions(transactions)
        self.unique_items = self._get_unique_items_from_transactions(transactions)

    @staticmethod
    def _get_unique_items_from_transactions(
        transactions: list[TransactionOpt],
    ) -> set[int]:
        unique_items = set()
        for transaction in transactions:
            for item in transaction.items:
                unique_items.add(item)
        return unique_items

    @staticmethod
    def _get_max_item_from_transactions(transactions: list[TransactionOpt]) -> int:
        """Get the maximum item ID from a list of transactions.

        Transaction items are sorted
        """
        return max(transaction.items[-1] for transaction in transactions)

    @classmethod
    def from_stream(cls, io: TextIO) -> Self:
        transactions = [
            TransactionOpt(items=[int(num) for num in line.strip().split()])
            for line in io.readlines()
        ]
        return cls(transactions)

    @classmethod
    def from_lists(cls, item_lists: list[list[int]]) -> Self:
        return cls([TransactionOpt(items) for items in item_lists])
