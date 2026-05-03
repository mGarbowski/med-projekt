from lcm_opt.itemset import ItemsetOpt


class TestItemset:
    def test_to_spmf_line(self):
        itemset = ItemsetOpt(items=[1, 2, 3], support=5)
        assert itemset.to_spmf_line() == "1 2 3 #SUP: 5"
