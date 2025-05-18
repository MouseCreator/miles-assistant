from typing import List

from src.miles.core.matcher.comand_defintion import CommandDefinition


class CommandPool:
    definitions: List[CommandDefinition]

    def __init__(self):
        self.definitions = []

    def append(self, command: CommandDefinition):
        self.definitions.append(command)

    def extend(self, commands: List[CommandDefinition]):
        self.definitions.extend(commands)

    def __iter__(self):
        return self.definitions.__iter__()
