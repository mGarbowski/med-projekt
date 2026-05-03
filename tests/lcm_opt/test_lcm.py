import pytest

from lcm_opt.itemset import ItemsetOpt
from lcm_opt.dataset import DatasetOpt
from lcm_opt.lcm import LCMAlgorithmOpt
from lcm_opt.transaction import TransactionOpt
from base.output import LCMOutputInMemory


class TestLcm:
    def test_initial_occurrence_delivery(self):
        t1 = TransactionOpt((1, 3, 4))
        t2 = TransactionOpt((2, 3, 6))
        t3 = TransactionOpt((1, 2, 3, 6))
        t4 = TransactionOpt((2, 6))
        t5 = TransactionOpt((1, 2, 3, 6))
        dataset = DatasetOpt([t1, t2, t3, t4, t5])

        expected_buckets = [
            [],
            [t1, t3, t5],
            [t2, t3, t4, t5],
            [t1, t2, t3, t5],
            [t1],
            [],
            [t2, t3, t4, t5],
        ]

        buckets = LCMAlgorithmOpt._initial_occurrence_delivery(dataset)

        assert buckets == expected_buckets

    def test_intersect_transactions(self):
        t1 = TransactionOpt((1, 3, 4))
        t2 = TransactionOpt((1, 2, 3))
        t3 = TransactionOpt((1, 4, 8, 9))
        t4 = TransactionOpt((1, 2, 5))
        transactions = [t1, t2, t3, t4]

        intersected = LCMAlgorithmOpt.intersect_transactions(transactions, 3)
        expected = [
            TransactionOpt((1, 3, 4), offset=1),
            TransactionOpt((1, 2, 3), offset=2),
        ]
        assert intersected == expected

    def test_intersect_transactions_having_offset_and_merging(self):
        t1 = TransactionOpt((1, 3, 4), offset=1)
        t2 = TransactionOpt((1, 2, 3, 4), offset=3)
        t3 = TransactionOpt((1, 4, 8, 9), offset=2)
        t4 = TransactionOpt((1, 2, 5), offset=1)
        transactions = [t1, t2, t3, t4]

        # interior_intersection: {1, 3, 4} & {1, 2, 3, 4} = {1, 3, 4}
        expected_merged_transaction = TransactionOpt(
            items=(1, 3, 4), 
            offset=2, 
            weight=2, 
            interior_intersection={1, 3, 4}
        )
        
        expected = [expected_merged_transaction]
        intersected = LCMAlgorithmOpt.intersect_transactions(transactions, 4)

        assert intersected == expected

    def test_is_item_in_all_transactions_except_first(self):
        t1 = TransactionOpt((1, 2, 4))
        t2 = TransactionOpt((1, 2, 3))
        t3 = TransactionOpt((1, 3, 8, 9))
        t4 = TransactionOpt((1, 2, 3))
        transactions = [t1, t2, t3, t4]
        assert LCMAlgorithmOpt.is_item_in_all_transactions_except_first(transactions, 1)
        assert not LCMAlgorithmOpt.is_item_in_all_transactions_except_first(
            transactions, 2
        )
        assert LCMAlgorithmOpt.is_item_in_all_transactions_except_first(transactions, 3)

    def _dataset_with_items(self, n_items: int) -> DatasetOpt:
        return DatasetOpt.from_lists([(1, 2, 3) for _ in range(n_items)])

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
            LCMAlgorithmOpt._convert_relative_support_to_absolute(
                relative_support,
                self._dataset_with_items(dataset_size),
            )
            == expected_absolute
        )

    def test_example_dataset(self, tmp_path):
        input_file = tmp_path / "input.txt"

        input_file.write_text(
            "1 3 4\n"
            "2 3 5\n"
            "1 2 3 5\n"
            "2 5\n"
            "1 2 3 5\n"
        )
        output_file = tmp_path / "output.txt"
        output = LCMOutputInMemory(output_file)
        lcm = LCMAlgorithmOpt(0.4, input_file, output)
        lcm.run()
        result = output.itemsets

        expected = [
            ItemsetOpt([1, 3], 3),
            ItemsetOpt([1, 2, 3, 5], 2),
            ItemsetOpt([2, 5], 4),
            ItemsetOpt([2, 3, 5], 3),
            ItemsetOpt([3], 4),
        ]
        assert result == expected
