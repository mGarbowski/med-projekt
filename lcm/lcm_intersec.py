import math

from base.abstract_lcm import AbstractLCM
from base.output import LCMOutput
from .itemset import Itemset
from .utils import contains_after
from .transaction import TransactionIntersec
from .dataset import DatasetIntersec


# TODO abstract output
class LCMAlgorithmIntersec(AbstractLCM):
    """Optimized implementation of Linear time Closed itemset Miner algorithm.

    For finding frequent, closed itemsets in a transaction database.
    """

    def __init__(
        self,
        relative_minimum_support: float,
        dataset: DatasetIntersec,
        output: LCMOutput,
    ):
        if not (0 <= relative_minimum_support <= 1):
            raise ValueError("Relative minimum support value must be between 0 and 1")

        self.output = output
        self.frequent_count = 0
        self.minimum_support = self._convert_relative_support_to_absolute(
            relative_minimum_support, dataset
        )
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
        self.backtracking_lcm([], self.dataset.transactions, all_frequent_items, -1)

    def backtracking_lcm(
        self,
        prefix: list[int],
        transactions_with_prefix: list[TransactionIntersec],
        frequent_items: list[int],
        prefix_tail_idx: int,
    ):
        for idx, item in enumerate(frequent_items):
            if len(prefix) > 0 and contains_after(prefix, item, prefix_tail_idx):
                continue

            transactions_of_union = self.intersect_transactions(
                transactions_with_prefix, item
            )

            if self.is_ppc_extension(prefix, transactions_of_union, item):
                itemset = [i for i in prefix if i < item]
                itemset.append(item)
                item_tail_idx = len(itemset) - 1

                for item_k in frequent_items[idx + 1 :]:
                    if self.is_item_in_all_transactions(transactions_of_union, item_k):
                        itemset.append(item_k)

                support = sum(t.weight for t in transactions_of_union)
                self.output.save(Itemset(items=itemset, support=support))

                self.anytime_database_reduction(
                    transactions_of_union, idx, frequent_items, item
                )

                new_frequent_items = []
                for item_k in frequent_items[idx + 1 :]:
                    support_k = sum(t.weight for t in self.buckets[item_k])
                    if support_k >= self.minimum_support:
                        new_frequent_items.append(item_k)

                self.backtracking_lcm(
                    itemset, transactions_of_union, new_frequent_items, item_tail_idx
                )

    def anytime_database_reduction(
        self,
        transactions_of_union: list[TransactionIntersec],
        idx_in_frequent_items: int,
        frequent_items: list[int],
        item_e: int,
    ):
        for item in frequent_items[idx_in_frequent_items + 1 :]:
            self.buckets[item] = []

        for transaction in transactions_of_union:
            for item in transaction.items[: transaction.offset : -1]:
                if item > item_e and item in frequent_items:
                    self.buckets[item].append(transaction)

    @staticmethod
    def intersect_transactions(
        transactions: list[TransactionIntersec], item: int
    ) -> list[TransactionIntersec]:
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
                    TransactionIntersec.with_offset(transaction, item_position)
                )

        return LCMAlgorithmIntersec.merge_transactions(transactions_of_union)

    @staticmethod
    def is_ppc_extension(
        prefix: list[int], transactions_of_union: list[TransactionIntersec], e: int
    ) -> bool:
        """Check if union(prefix, {e}) is a prefix-preserving closure extension"""
        first_t = transactions_of_union[0]
        for item in first_t.interior_intersection:
            if (
                item < e
                and (len(prefix) == 0 or item not in prefix)  # TODO binary search
                and LCMAlgorithmIntersec.is_item_in_all_transactions_except_first(
                    transactions_of_union, item
                )
            ):
                return False
        return True

    @staticmethod
    def is_item_in_all_transactions_except_first(
        transactions: list[TransactionIntersec], item: int
    ):
        for transaction in transactions[1:]:
            if item not in transaction.interior_intersection:
                return False
        return True

    @staticmethod
    def is_item_in_all_transactions(
        transactions: list[TransactionIntersec], item: int
    ) -> bool:
        # TODO binary search
        return all(
            item in transaction.interior_intersection for transaction in transactions
        )

    @staticmethod
    def merge_transactions(
        transactions: list[TransactionIntersec],
    ) -> list[TransactionIntersec]:
        """Merges identical transactions"""
        merged_dict: dict[tuple[int, ...], TransactionIntersec] = {}

        for t in transactions:
            key = t.get_active_items_tuple()

            if key not in merged_dict:
                merged_dict[key] = t
            else:
                # merge duplicate transactions
                existing_t = merged_dict[key]
                existing_t.weight += t.weight
                existing_t.interior_intersection.intersection_update(
                    t.interior_intersection
                )

        return list(merged_dict.values())  # list of unique transactions after merge

    @staticmethod
    def _initial_occurrence_delivery(
        dataset: DatasetIntersec,
    ) -> list[list[TransactionIntersec]]:
        buckets = [[] for _ in range(dataset.max_item + 1)]

        for transaction in dataset.transactions:
            for item in transaction.items:
                buckets[item].append(transaction)

        return buckets

    @staticmethod
    def _convert_relative_support_to_absolute(
        relative_support: float, dataset: DatasetIntersec
    ) -> int:
        """Converting percentage to number of items.

        Rounding logic consistent with SPMF.
        """
        return math.ceil(relative_support * len(dataset.transactions))
