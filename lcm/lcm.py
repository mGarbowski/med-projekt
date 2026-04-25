from .utils import contains_after
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
        for transaction in self.dataset.transactions:
            transaction.remove_infrequent_items(self.buckets, self.minimum_support)

        all_frequent_items = sorted(
            [
                item
                for item in self.dataset.unique_items
                if len(self.buckets[item]) >= self.minimum_support
            ]
        )
        pass

    def backtracking_lcm(
        self,
        prefix: list[int],
        transactions_with_prefix: list[Transaction],
        frequent_items: list[int],
        prefix_tail_idx: int,
    ):
        for idx, item in enumerate(frequent_items):
            if len(prefix) > 0 and contains_after(prefix, item, prefix_tail_idx):
                continue

            pass

    @staticmethod
    def intersect_transactions(
        transactions: list[Transaction], item: int
    ) -> list[Transaction]:
        """Get transactions containing the union of items
        transactions is a list of transactions of itemset P
        this calculates the transaction list for itemset union(P, {item})
        and truncates the transactions to keep what appears after item
        """
        transactions_of_union = []
        for transaction in transactions:
            item_position = transaction.item_position(item)  # search after offset
            if item_position is not None:
                transactions_of_union.append(
                    Transaction.with_offset(transaction, item_position)
                )

        return transactions_of_union

    @staticmethod
    def _initial_occurrence_delivery(
        dataset: Dataset,
    ) -> tuple[list[Transaction], ...]:
        buckets = tuple([] for _ in range(dataset.max_item + 1))

        for transaction in dataset.transactions:
            for item in transaction.items:
                buckets[item].append(transaction)

        return buckets
