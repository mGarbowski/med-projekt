from io import StringIO

from lcm.dataset import Dataset
from lcm.transaction import Transaction


class TestDataset:
    def test_from_lists(self):
        item_lists = [[1, 3, 4], [2, 3]]
        expected_transactions = [Transaction([1, 3, 4]), Transaction([2, 3])]
        dataset = Dataset.from_lists(item_lists)
        assert dataset.transactions == expected_transactions

    def test_from_stream(self):
        stream = StringIO("""1 3 4
2 3 5
1 2 3 5
2 5 
1 2 3 5""")
        dataset = Dataset.from_stream(stream)
        expected_dataset = Dataset.from_lists(
            [
                [1, 3, 4],
                [2, 3, 5],
                [1, 2, 3, 5],
                [2, 5],
                [1, 2, 3, 5],
            ]
        )
        assert dataset.transactions == expected_dataset.transactions
