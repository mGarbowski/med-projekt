from abc import ABC, abstractmethod


class AbstractItemset(ABC):
    @abstractmethod
    def to_spmf_line(self) -> str:
        pass
