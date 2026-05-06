from typing import TextIO, Self

from .transaction import Transaction, TransactionIntersec


class Dataset:
    def __init__(self, transactions: list[Transaction]):
        self.transactions = transactions
        self.max_item = self._get_max_item_from_transactions(transactions)
        self.unique_items = self._get_unique_items_from_transactions(transactions)

    @staticmethod
    def _get_unique_items_from_transactions(
        transactions: list[Transaction],
    ) -> set[int]:
        unique_items = set()
        for transaction in transactions:
            for item in transaction.items:
                unique_items.add(item)
        return unique_items

    @staticmethod
    def _get_max_item_from_transactions(transactions: list[Transaction]) -> int:
        """Get the maximum item ID from a list of transactions.

        Transaction items are sorted
        """
        return max(transaction.items[-1] for transaction in transactions)

    @classmethod
    def from_stream(cls, io: TextIO) -> Self:
        transactions = [
            Transaction(items=[int(num) for num in line.strip().split()])
            for line in io.readlines()
        ]
        return cls(transactions)

    @classmethod
    def from_lists(cls, item_lists: list[list[int]]) -> Self:
        return cls([Transaction(items) for items in item_lists])


class DatasetIntersec:
    def __init__(self, transactions: list[TransactionIntersec]):
        self.transactions = transactions
        self.max_item = self._get_max_item_from_transactions(transactions)
        self.unique_items = self._get_unique_items_from_transactions(transactions)

    @staticmethod
    def _get_unique_items_from_transactions(
        transactions: list[TransactionIntersec],
    ) -> set[int]:
        unique_items = set()
        for transaction in transactions:
            for item in transaction.items:
                unique_items.add(item)
        return unique_items

    @staticmethod
    def _get_max_item_from_transactions(transactions: list[TransactionIntersec]) -> int:
        """Get the maximum item ID from a list of transactions.

        Transaction items are sorted
        """
        return max(transaction.items[-1] for transaction in transactions)

    @classmethod
    def from_stream(cls, io: TextIO) -> Self:
        transactions = [
            TransactionIntersec(items=[int(num) for num in line.strip().split()])
            for line in io.readlines()
        ]
        return cls(transactions)

    @classmethod
    def from_lists(cls, item_lists: list[list[int]]) -> Self:
        return cls([TransactionIntersec(items) for items in item_lists])
