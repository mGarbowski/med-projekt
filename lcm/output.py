from abc import ABC, abstractmethod
from pathlib import Path
from typing import override

from .itemset import Itemset


class LCMOutput(ABC):
    @abstractmethod
    def save(self, itemset: Itemset):
        pass


class LCMOutputInMemory(LCMOutput):
    def __init__(self):
        self.itemsets = []

    @override
    def save(self, itemset: Itemset):
        self.itemsets.append(itemset)


class LCMOutputToFile(LCMOutput):
    def __init__(self, output_file: Path):
        self.output_file = output_file
        self.output_file.write_text("")

    @override
    def save(self, itemset: Itemset):
        with open(self.output_file, "at") as f:
            f.write(f"{itemset.to_spmf_line()}\n")
