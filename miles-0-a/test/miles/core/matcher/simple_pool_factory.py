from src.miles.core.command.command import Command, RootComponent
from src.miles.core.matcher.comand_defintion import CommandDefinition, CommandNamespace
from src.miles.core.matcher.command_pool import CommandPool


class SimpleCommandPoolFactory:

    def __init__(self):
        self._command_pool = CommandPool()

    def append(self, root: RootComponent,
               namespace: str | None,
               plugin: str | None,
               command_name: str | None):
        namespace_obj = CommandNamespace(plugin, namespace, command_name)
        command = Command(root)
        command_def = CommandDefinition(namespace_obj, command)
        self._command_pool.append(command_def)

    def get(self):
        return self._command_pool