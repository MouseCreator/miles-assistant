from typing import Callable, List

from src.miles.core.command.command import Command, WordComponent


class CommandNamespace:
    def __init__(self, plugin_name: str, namespace_name: str, command_name: str):
        self.plugin_name = plugin_name
        self.namespace_name = namespace_name
        self.command_name = command_name

    def get_arguments(self) -> List[WordComponent]:
        return []

class CommandDefinitionContext:
    pass

class CommandDefinition:
    def __init__(self, namespace: CommandNamespace, command: Command, on_match: Callable):
        self._namespace = namespace
        self._command = command
        self._on_match = on_match
    def get_namespace(self) -> CommandNamespace:
        return self._namespace
    def get_command(self) -> Command:
        return self._command
    def on_match(self, context : CommandDefinitionContext):
        self._on_match(context)