from lcm.dataset import Dataset
from lcm.lcm import LCMAlgorithm
from lcm.transaction import Transaction


class TestLcm:
    def test_initial_occurrence_delivery(self):
        t1 = Transaction([1, 3, 4])
        t2 = Transaction([2, 3, 6])
        t3 = Transaction([1, 2, 3, 6])
        t4 = Transaction([2, 6])
        t5 = Transaction([1, 2, 3, 6])
        dataset = Dataset([t1, t2, t3, t4, t5])

        expected_buckets = (
            [],
            [t1, t3, t5],
            [t2, t3, t4, t5],
            [t1, t2, t3, t5],
            [t1],
            [],
            [t2, t3, t4, t5],
        )

        buckets = LCMAlgorithm._initial_occurrence_delivery(dataset)

        assert buckets == expected_buckets
