import pytest

from lcm.itemset import Itemset
from lcm.dataset import Dataset
from lcm.lcm import LCMAlgorithm
from lcm.transaction import Transaction
from lcm.output import LCMOutputInMemory


class TestLcm:
    def test_initial_occurrence_delivery(self):
        t1 = Transaction([1, 3, 4])
        t2 = Transaction([2, 3, 6])
        t3 = Transaction([1, 2, 3, 6])
        t4 = Transaction([2, 6])
        t5 = Transaction([1, 2, 3, 6])
        dataset = Dataset([t1, t2, t3, t4, t5])

        expected_buckets = [
            [],
            [t1, t3, t5],
            [t2, t3, t4, t5],
            [t1, t2, t3, t5],
            [t1],
            [],
            [t2, t3, t4, t5],
        ]

        buckets = LCMAlgorithm._initial_occurrence_delivery(dataset)

        assert buckets == expected_buckets

    def test_intersect_transactions(self):
        t1 = Transaction([1, 3, 4])
        t2 = Transaction([1, 2, 3])
        t3 = Transaction([1, 4, 8, 9])
        t4 = Transaction([1, 2, 5])
        transactions = [t1, t2, t3, t4]

        intersected = LCMAlgorithm.intersect_transactions(transactions, 3)
        expected = [
            Transaction([1, 3, 4], offset=1, original_transaction=t1),
            Transaction([1, 2, 3], offset=2, original_transaction=t2),
        ]
        assert intersected == expected

    def test_interset_transactions_having_offset(self):
        t1 = Transaction([1, 3, 4], offset=1)
        t2 = Transaction([1, 2, 3, 4], offset=3)
        t3 = Transaction([1, 4, 8, 9], offset=2)
        t4 = Transaction([1, 2, 5], offset=1)
        transactions = [t1, t2, t3, t4]

        expected = [
            Transaction([1, 3, 4], offset=2, original_transaction=t1),
            Transaction([1, 2, 3, 4], offset=3, original_transaction=t2),
        ]

        intersected = LCMAlgorithm.intersect_transactions(transactions, 4)

        assert intersected == expected

    def test_is_item_in_all_transactions_except_first(self):
        t1 = Transaction([1, 2, 4])
        t2 = Transaction([1, 2, 3])
        t3 = Transaction([1, 3, 8, 9])
        t4 = Transaction([1, 2, 3])
        transactions = [t1, t2, t3, t4]
        assert LCMAlgorithm.is_item_in_all_transactions_except_first(transactions, 1)
        assert not LCMAlgorithm.is_item_in_all_transactions_except_first(
            transactions, 2
        )
        assert LCMAlgorithm.is_item_in_all_transactions_except_first(transactions, 3)

    def test_is_item_in_all_transactions_except_first_ignores_offsets(self):
        """It should perform search in the original transaction so that offsets are ignored."""
        t1 = Transaction([1, 2, 4])
        t2 = Transaction([1, 2, 3])
        t3 = Transaction([1, 3, 8, 9])
        t4 = Transaction([1, 2, 3])
        transactions = [
            Transaction.with_offset(t1, 2),
            Transaction.with_offset(t2, 2),
            Transaction.with_offset(t3, 3),
            Transaction.with_offset(t4, 2),
        ]

        assert LCMAlgorithm.is_item_in_all_transactions_except_first(transactions, 1)
        assert not LCMAlgorithm.is_item_in_all_transactions_except_first(
            transactions, 2
        )
        assert LCMAlgorithm.is_item_in_all_transactions_except_first(transactions, 3)

    def _dataset_with_items(self, n_items: int) -> Dataset:
        return Dataset.from_lists([[1, 2, 3] for _ in range(n_items)])

    @pytest.mark.parametrize(
        ("relative_support", "dataset_size", "expected_absolute"),
        [
            (0.40, 5, 2),
            (0.41, 5, 3),
            (0.5, 5, 3),
            (0.6, 5, 3),
            (0.61, 5, 4),
        ],
    )
    def test_relative_to_absolute_support(
        self,
        relative_support: float,
        dataset_size: int,
        expected_absolute: int,
    ):
        """Ensure rounding is consistent with SPMF implementation."""
        assert (
            LCMAlgorithm._convert_relative_support_to_absolute(
                relative_support,
                self._dataset_with_items(dataset_size),
            )
            == expected_absolute
        )

    def test_example_dataset(self):
        dataset = Dataset.from_lists(
            [
                [1, 3, 4],
                [2, 3, 5],
                [1, 2, 3, 5],
                [2, 5],
                [1, 2, 3, 5],
            ]
        )
        output = LCMOutputInMemory()
        lcm = LCMAlgorithm(0.4, dataset, output)
        lcm.run()
        result = output.itemsets

        expected = [
            Itemset([1, 3], 3),
            Itemset([1, 2, 3, 5], 2),
            Itemset([2, 5], 4),
            Itemset([2, 3, 5], 3),
            Itemset([3], 4),
        ]
        assert result == expected
