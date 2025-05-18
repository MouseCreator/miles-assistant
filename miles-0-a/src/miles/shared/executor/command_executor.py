from abc import ABC, abstractmethod
from typing import Dict

from src.miles.shared.executor.command_structure import CommandStructure


class CommandExecutor(ABC):
    @abstractmethod
    def on_recognize(self, command_structure: CommandStructure, context):
        pass


class CommandExecutorsMap:
    _map: Dict[str, CommandExecutor]

    def __init__(self):
        self._map = {}

    def add(self, command: str, executor: CommandExecutor):
        self._map[command] = executor

    def get(self, command: str) -> CommandExecutor:
        return self._map[command]
