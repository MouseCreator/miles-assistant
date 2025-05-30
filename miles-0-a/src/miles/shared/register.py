from typing import List

from src.miles.core.priority.priority_config import PriorityStrategy
from src.miles.core.recognizer.matching_definition import MatchingDefinition
from src.miles.shared.certainty import SortCertaintyEffect, CertaintyEffect
from src.miles.shared.context_analyzer import TypedContextAnalyzer, DefaultWordContextAnalyzerFactory, \
    WordContextAnalyzerFactory
from src.miles.shared.executor.command_executor import CommandExecutor
from src.miles.shared.priority.dynamic_priority import DynamicPriorityRule
from src.miles.shared.priority.priority_rule import PriorityRule
from src.miles.utils.singleton import Singleton


class _PrefixSet:
    _prefixes: List[str]

    def __init__(self):
        self._prefixes = []

    def remember_and_validate(self, new_prefix: str):
        for old_prefix in self._prefixes:
            if old_prefix.startswith(new_prefix):
                raise ValueError(f'Prefix conflict: "{new_prefix}" is part of "{old_prefix}"')
            if new_prefix.startswith(old_prefix):
                raise ValueError(f'Prefix conflict: "{old_prefix}" is part of "{new_prefix}"')
        self._prefixes.append(new_prefix)


class CommandInitializer:
    def __init__(self, name: str, syntax: str, executor: CommandExecutor):
        self.name = name
        self.syntax = syntax
        self.executor = executor


class NamespaceInitializer:
    _static_priority_rules: List[PriorityRule]
    _matchings: List[MatchingDefinition]

    def __init__(self, name: str, prefix: str):
        self._name = name
        self._prefix = prefix
        self._commands = []
        self._static_priority_rules = []
        self._dynamic_priority_rules = []
        self._matchings = []
        self._priority_strategy = PriorityStrategy.ALL_DEFAULT
        self._default_priority = 0
        self._word_analyzer_factory = DefaultWordContextAnalyzerFactory()
        self._certainty_effect = SortCertaintyEffect()

    def add_command(self, name: str, syntax: str, executor: CommandExecutor):
        command = CommandInitializer(name, syntax, executor)
        self._commands.append(command)

    def set_priority_strategy(self, ps: PriorityStrategy):
        self._priority_strategy = ps

    def get_priority_strategy(self) -> PriorityStrategy:
        return self._priority_strategy

    def set_default_priority(self, priority: int):
        self._default_priority = priority

    def get_default_priority(self) -> int:
        return self._default_priority

    def extend_commands(self, commands: List[CommandInitializer]):
        self._commands.extend(commands)

    def add_matching(self, name: str, analyzer: TypedContextAnalyzer):
        matching = MatchingDefinition(name, analyzer)
        self._matchings.append(matching)

    def extend_matching(self, matchings: List[MatchingDefinition]):
        self._matchings.extend(matchings)

    def get_matchings(self) -> List[MatchingDefinition]:
        return list(self._matchings)

    def get_commands(self) -> List[CommandInitializer]:
        return list(self._commands)

    def add_static_priority_rule(self, rule: PriorityRule):
        self._static_priority_rules.append(rule)

    def add_dynamic_priority_rule(self, rule: DynamicPriorityRule):
        self._dynamic_priority_rules.append(rule)

    def get_name(self):
        return self._name

    def get_prefix(self):
        return self._prefix

    def get_static_priorities(self):
        return self._static_priority_rules

    def get_dynamic_priorities(self) -> List[DynamicPriorityRule]:
        return self._dynamic_priority_rules

    def get_word_analyzer_factory(self) -> WordContextAnalyzerFactory:
        return self._word_analyzer_factory

    def set_word_analyzer_factory(self, factory: WordContextAnalyzerFactory):
        self._word_analyzer_factory = factory

    def get_certainty_effect(self):
        return self._certainty_effect

    def set_certainty_effect(self, ce: CertaintyEffect):
        self._certainty_effect = ce


class PluginRegister:
    _name: str

    def __init__(self, name: str, display_name: str, _prefixes: _PrefixSet):
        self._name = name
        self._prefixes = _prefixes
        if display_name is None:
            display_name = name
        self._display_name = display_name
        self._namespaces = []

    def get_name(self):
        return self._name

    def get_display_name(self):
        return self._display_name

    def add_namespace(self, name: str, prefix: str) -> NamespaceInitializer:
        namespace = NamespaceInitializer(name, prefix)
        self._prefixes.remember_and_validate(namespace.get_prefix())
        self._namespaces.append(namespace)
        return namespace

    def get_namespaces(self) -> List[NamespaceInitializer]:
        return list(self._namespaces)


class MilesRegister(metaclass=Singleton):
    _plugins: List[PluginRegister]

    def __init__(self):
        self._plugins = []
        self._prefix_set = _PrefixSet()

    def _has_plugin_named(self, name: str):
        for p in self._plugins:
            if p.get_name() == name:
                return True
        return False

    def create_plugin_register(self, plugin_name: str, display_name: str | None = None) -> PluginRegister:
        plugin = PluginRegister(plugin_name, display_name, self._prefix_set)

        if self._has_plugin_named(plugin_name):
            raise ValueError(f'Plugin "{plugin_name}" has already been registered')

        self._plugins.append(plugin)
        return plugin

    def all_plugins(self) -> List[PluginRegister]:
        return list(self._plugins)
