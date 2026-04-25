from lcm.itemset import Itemset


class TestItemset:
    def test_to_spmf_line(self):
        itemset = Itemset(items=[1, 2, 3], support=5)
        assert itemset.to_spmf_line() == "1 2 3 #SUP: 5"
