from typing import List

from src.miles.core.matcher.comand_defintion import CommandDefinition


class CommandPool:
    definitions: List[CommandDefinition]

    def __init__(self):
        self.definitions = []

    def append(self, command: CommandDefinition):
        self.definitions.append(command)

    def append_all(self, commands: List[CommandDefinition]):
        for c in commands:
            self.definitions.append(c)
            
    def __iter__(self):
        return self.definitions
