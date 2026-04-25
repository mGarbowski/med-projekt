from .itemset import Itemset


class Itemsets:
    levels: list[list[Itemset]]

    def __init__(self):
        self.levels = []
