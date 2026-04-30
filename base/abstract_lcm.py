from abc import ABC, abstractmethod


class AbstractLCM(ABC):
    """Abstract base class for frequent itemset mining algorithms."""

    @abstractmethod
    def run(self) -> None:
        """Executes the algorithm."""
        pass
