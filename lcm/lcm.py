from .transaction import Transaction
from .dataset import Dataset
from .itemsets import Itemsets


class LCMAlgorithm:
    """Implementation of Linear time Closed itemset Miner algorithm.

    For finding frequent, closed itemsets in a transaction database.
    """

    def __init__(self, relative_minimum_support: float, dataset: Dataset):
        if not (0 <= relative_minimum_support <= 1):
            raise ValueError("Relative minimum support value must be between 0 and 1")

        self.discovered_itemsets = Itemsets()
        self.frequent_count = 0
        self.minimum_support = int(relative_minimum_support * len(dataset.transactions))
        self.dataset = dataset
        self.buckets = self._initial_occurrence_delivery(dataset)

    def run(self):
        pass

    @staticmethod
    def _initial_occurrence_delivery(
        dataset: Dataset,
    ) -> tuple[list[Transaction], ...]:
        buckets = tuple([] for _ in range(dataset.max_item + 1))

        for transaction in dataset.transactions:
            for item in transaction.items:
                buckets[item].append(transaction)

        return buckets
