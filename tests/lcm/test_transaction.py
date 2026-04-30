from copy import deepcopy

from lcm.transaction import Transaction


class TestTransaction:
    def test_remove_infrequent_items(self):
        t1 = Transaction([1, 3, 4])
        t2 = Transaction([2, 3])
        t3 = Transaction([1, 2, 3, 6])
        t4 = Transaction([2, 6])
        t5 = Transaction([2, 3, 6])

        buckets = [
            [],
            [t1, t3],
            [t2, t3, t4, t5],
            [t1, t2, t3, t5],
            [t1],
            [],
            [t3, t4, t5],
        ]

        t3_copy = deepcopy(t3)
        t3_copy.remove_infrequent_items(buckets, min_support=1)
        assert t3_copy.items == [1, 2, 3, 6]

        t3_copy = deepcopy(t3)
        t3_copy.remove_infrequent_items(buckets, min_support=2)
        assert t3_copy.items == [1, 2, 3, 6]

        t3_copy = deepcopy(t3)
        t3_copy.remove_infrequent_items(buckets, min_support=3)
        assert t3_copy.items == [2, 3, 6]

        t3_copy = deepcopy(t3)
        t3_copy.remove_infrequent_items(buckets, min_support=4)
        assert t3_copy.items == [2, 3]

        t3_copy = deepcopy(t3)
        t3_copy.remove_infrequent_items(buckets, min_support=5)
        assert t3_copy.items == []

    def test_item_position(self):
        t = Transaction([1, 4, 6, 8, 9])
        assert t.item_position(0) is None
        assert t.item_position(5) is None
        assert t.item_position(1) == 0
        assert t.item_position(4) == 1
        assert t.item_position(6) == 2
        assert t.item_position(8) == 3
        assert t.item_position(9) == 4

        t = Transaction([1, 4, 6, 8, 9], offset=2)
        assert t.item_position(0) is None
        assert t.item_position(5) is None
        assert t.item_position(1) is None
        assert t.item_position(4) is None
        assert t.item_position(6) == 2
        assert t.item_position(8) == 3
        assert t.item_position(9) == 4
