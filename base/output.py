from abc import ABC, abstractmethod
from pathlib import Path
from typing import override

from .abstract_itemset import AbstractItemset


class LCMOutput(ABC):
    @abstractmethod
    def save(self, itemset: AbstractItemset):
        pass

    def close(self):
        pass


class LCMOutputInMemory(LCMOutput):
    def __init__(self, output_file: Path):
        self.itemsets = []
        self.output_file = output_file

    @override
    def save(self, itemset: AbstractItemset):
        self.itemsets.append(itemset)

    @override
    def close(self):
        with open(self.output_file, "w") as f:
            for itemset in self.itemsets:
                f.write(f"{itemset.to_spmf_line()}\n")


class LCMOutputToFile(LCMOutput):
    def __init__(self, output_file: Path):
        self.output_file = output_file
        self.file_handle = open(self.output_file, "w")

    @override
    def save(self, itemset: AbstractItemset):
        self.file_handle.write(f"{itemset.to_spmf_line()}\n")

    @override
    def close(self):
        self.file_handle.close()
