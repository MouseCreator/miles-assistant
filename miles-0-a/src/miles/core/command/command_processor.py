from abc import ABC, abstractmethod

from src.miles.core.command.command import Command


class CommandProcessor(ABC):

    @abstractmethod
    def process(self, command_string: str) -> Command:
        pass

