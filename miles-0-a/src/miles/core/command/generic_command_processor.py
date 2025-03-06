from src.miles.core.command.command import Command
from src.miles.core.command.command_processor import CommandProcessor


class GenericCommandProcessor(CommandProcessor):
    def process(self, command_string: str) -> Command:
        pass
