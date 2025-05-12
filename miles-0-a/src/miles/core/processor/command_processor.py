from abc import ABC, abstractmethod

from src.miles.core.processor.command_structure import CommandStructure


class CommandProcessor(ABC):
    @abstractmethod
    def on_recognize(self, command_structure: CommandStructure):
        pass