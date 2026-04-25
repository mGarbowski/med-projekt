from dataclasses import dataclass


@dataclass
class Transaction:
    items: list[int]

    def __eq__(self, other):
        return self.items == other.items
