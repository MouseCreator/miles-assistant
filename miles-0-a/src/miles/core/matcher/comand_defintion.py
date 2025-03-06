from typing import Callable

from src.miles.core.command.command import Command


class CommandNamespace:
    pass

class CommandDefinitionContext:
    pass

class CommandDefinition:
    def __init__(self, namespace: CommandNamespace, name: str, command: Command, on_match: Callable):
        self._namespace = namespace
        self._name = name
        self._command = command
        self._on_match = on_match
    def get_namespace(self) -> CommandNamespace:
        return self._namespace
    def get_name(self) -> str:
        return self._name
    def get_command(self) -> Command:
        return self._command
    def on_match(self, context : CommandDefinitionContext):
        self._on_match(context)