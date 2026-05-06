from io import StringIO

from lcm_opt.dataset import DatasetOpt
from lcm_opt.transaction import TransactionOpt


class TestDataset:
    def test_from_lists(self):
        item_lists: list[tuple[int, ...]] = [(1, 3, 4), (2, 3)]
        expected_transactions = [TransactionOpt((1, 3, 4)), TransactionOpt((2, 3))]
        dataset = DatasetOpt.from_lists(item_lists)
        assert dataset.transactions == expected_transactions

    def test_from_stream(self):
        stream = StringIO("""1 3 4
2 3 5
1 2 3 5
2 5 
1 2 3 5""")
        dataset = DatasetOpt.from_stream(stream)
        expected_dataset = DatasetOpt.from_lists(
            [
                (1, 3, 4),
                (2, 3, 5),
                (1, 2, 3, 5),
                (2, 5),
                (1, 2, 3, 5),
            ]
        )
        assert dataset.transactions == expected_dataset.transactions

    def test_get_max_item_from_transactions(self):
        transactions = [TransactionOpt((1, 3, 4)), TransactionOpt((2, 3))]
        assert DatasetOpt._get_max_item_from_transactions(transactions) == 4

    def test_is_initialized_with_max_item(self):
        transactions = [TransactionOpt((1, 3, 4)), TransactionOpt((2, 3))]
        dataset = DatasetOpt(transactions)
        assert dataset.max_item == 4

    def test_get_unique_items_from_transactions(self):
        transactions = [TransactionOpt((1, 3, 4)), TransactionOpt((2, 3))]
        unique_items = DatasetOpt._get_unique_items_from_transactions(transactions)
        assert unique_items == {1, 2, 3, 4}

    def test_is_initialized_with_unique_items(self):
        transactions = [TransactionOpt((1, 3, 4)), TransactionOpt((2, 3))]
        dataset = DatasetOpt(transactions)
        assert dataset.unique_items == {1, 2, 3, 4}
