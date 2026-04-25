from dataclasses import dataclass
from typing import TextIO, Self

from .transaction import Transaction


@dataclass
class Dataset:
    transactions: list[Transaction]

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
