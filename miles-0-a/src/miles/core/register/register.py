from typing import List

from src.miles.utils.singleton import Singleton


class CommandInitializer:
    pass

class StaticPriorityRuleInitializer:
    pass

class DynamicPriorityRuleInitializer:
    pass

class NamespaceInitializer:
    def __init__(self, name: str, identifier: str):
        self._name = name
        self._identifier = identifier
        self._commands = []

    def add_command(self, command: CommandInitializer):
        self._commands.append(command)

    def extend_commands(self, commands: List[CommandInitializer]):
        self._commands.extend(commands)

    def get_commands(self):
        return list(self._commands)

    def add_static_priority_rule(self, command: StaticPriorityRuleInitializer):
        pass

    def add_dynamic_priority_rule(self, command: DynamicPriorityRuleInitializer):
        pass

class PluginRegister:
    _name: str

    def __init__(self, name: str, display_name: str | None=None):
        self._name = name
        if display_name is None:
            display_name = name
        self._display_name = display_name

    def get_name(self):
        return self._name

    def get_display_name(self):
        return self._display_name

    def add_namespace(self, namespace: NamespaceInitializer):
        pass

class MilesRegister(metaclass=Singleton):
    _plugins: List[PluginRegister]
    def __init__(self):
        self._plugins = []

    def _has_plugin_named(self, name: str):
        for p in self._plugins:
            if p.get_name() == name:
                return True
        return False

    def create_plugin_register(self, plugin_name: str, display_name: str | None = None) -> PluginRegister:
        plugin = PluginRegister(plugin_name, display_name)

        if self._has_plugin_named(plugin_name):
            raise ValueError(f'Plugin "{plugin_name}" has already been registered')

        self._plugins.append(plugin)
        return plugin
