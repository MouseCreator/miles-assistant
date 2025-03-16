from abc import ABC, abstractmethod


class PrintableStructure(ABC):
    @abstractmethod
    def sprint(self) -> str:
        pass

