from typing import Callable, List

from src.miles.core.command.command import Command, WordComponent


class CommandNamespace:
    def __init__(self, namespace_name: str, arguments: List[WordComponent]):
        self.namespace_name = namespace_name
        self._arguments = arguments

    def get_arguments(self) -> List[WordComponent]:
        return list(self._arguments)


class CommandDefinitionContext:
    pass


class CommandDefinition:
    def __init__(self, namespace: CommandNamespace, command: Command, on_match: Callable | None = None):
        self._namespace = namespace
        self._command = command
        self._on_match = on_match

    def get_namespace(self) -> CommandNamespace:
        return self._namespace

    def get_command(self) -> Command:
        return self._command

    def on_match(self, context: CommandDefinitionContext):
        if self._on_match is not None:
            self._on_match(context)
