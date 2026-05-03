import math
from pathlib import Path
from typing import override

from base.abstract_lcm import AbstractLCM
from base.output import LCMOutput
from .itemset import ItemsetOpt
from .utils import contains_after
from .transaction import TransactionOpt
from .dataset import DatasetOpt


class LCMAlgorithmOpt(AbstractLCM):
    """Optimized implementation of Linear time Closed itemset Miner algorithm.

    For finding frequent, closed itemsets in a transaction database.
    """

    def __init__(
        self, relative_minimum_support: float, input_file: Path, output: LCMOutput
    ):
        if not (0 <= relative_minimum_support <= 1):
            raise ValueError("Relative minimum support value must be between 0 and 1")

        self.output = output

        with open(input_file) as f:
            dataset = DatasetOpt.from_stream(f)
        self.dataset = dataset

        self.minimum_support = self._convert_relative_support_to_absolute(
            relative_minimum_support, dataset
        )
        
        self.buckets = self._initial_occurrence_delivery(dataset)

    @override
    def close(self) -> None:
        """Delegates closing/saving to the output handler."""
        self.output.close()

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
        transactions_with_prefix: list[TransactionOpt],
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

                support = sum([t.weight for t in transactions_of_union])
                self.output.save(ItemsetOpt(items=itemset, support=support))

                self.anytime_database_reduction(
                    transactions_of_union,
                    idx,
                    frequent_items,  # , item
                )

                new_frequent_items = [
                    item_k
                    for item_k in frequent_items[idx + 1 :]
                    if sum([t.weight for t in self.buckets[item_k]]) >= self.minimum_support
                ]

                self.backtracking_lcm(
                    itemset, transactions_of_union, new_frequent_items, item_tail_idx
                )

    def anytime_database_reduction(
        self,
        transactions_of_union: list[TransactionOpt],
        idx_in_frequent_items: int,
        frequent_items: list[int],
        # item_e: int,
    ):
        valid_targets = set(frequent_items[idx_in_frequent_items + 1 :])
        for item in valid_targets:
            self.buckets[item].clear()

        if not valid_targets:
            return

        # no need for item > item_e as valid_targets has only bigger elements
        for transaction in transactions_of_union:
            for item in transaction.items[transaction.offset + 1 :]:
                if item in valid_targets:
                    self.buckets[item].append(transaction)

    @staticmethod
    def intersect_transactions(
        transactions: list[TransactionOpt], item: int
    ) -> list[TransactionOpt]:
        """
        Get transactions containing the union of items
        transactions is a list of transactions of itemset P
        this calculates the transaction list for itemset union(P, {item})
        also merges identical transactions combining their weigth and interior_intersection
        """
        merged_dict = {}  # for groupping transactions, key is an active part of transaciton (tuple - hashable)

        for t in transactions:
            if item not in t.interior_intersection:
                continue

            pos = t.item_position(item)
            if pos is not None:
                key = t.items[pos:]  # active part of transaction

                if key not in merged_dict:
                    # first occurance, save data
                    merged_dict[key] = [
                        t.items,
                        pos,
                        t.weight,
                        [t.interior_intersection],
                    ]
                else:
                    # next occurance, update weight and add interior_intersection
                    merged_dict[key][2] += t.weight
                    merged_dict[key][3].append(t.interior_intersection)

        # now create TransactionOpt objects
        return [
            TransactionOpt(
                items=orig_items,
                offset=new_offset,
                weight=total_weight,
                interior_intersection=(
                    sets_list[0] if len(sets_list) == 1 else set.intersection(*sets_list)
                ),
            )
            for orig_items, new_offset, total_weight, sets_list in merged_dict.values()
        ]

    @staticmethod
    def is_ppc_extension(
        prefix: list[int], transactions_of_union: list[TransactionOpt], e: int
    ) -> bool:
        """Check if union(prefix, {e}) is a prefix-preserving closure extension"""
        first_t = transactions_of_union[0]
        check = LCMAlgorithmOpt.is_item_in_all_transactions_except_first  # local ref

        for item in first_t.interior_intersection:
            if item < e and item not in prefix and check(transactions_of_union, item):
                return False
        return True

    @staticmethod
    def is_item_in_all_transactions_except_first(
        transactions: list[TransactionOpt], item: int
    ):
        for transaction in transactions[1:]:
            if item not in transaction.interior_intersection:
                return False
        return True

    @staticmethod
    def is_item_in_all_transactions(
        transactions: list[TransactionOpt], item: int
    ) -> bool:
        for transaction in transactions:
            if item not in transaction.interior_intersection:
                return False
        return True

    @staticmethod
    def _initial_occurrence_delivery(
        dataset: DatasetOpt,
    ) -> list[list[TransactionOpt]]:
        buckets = [[] for _ in range(dataset.max_item + 1)]
        transactions = dataset.transactions

        for transaction in transactions:
            for item in transaction.items:
                buckets[item].append(transaction)

        return buckets

    @staticmethod
    def _convert_relative_support_to_absolute(
        relative_support: float, dataset: DatasetOpt
    ) -> int:
        """Converting percentage to number of items.

        Rounding logic consistent with SPMF.
        """
        return math.ceil(relative_support * len(dataset.transactions))
