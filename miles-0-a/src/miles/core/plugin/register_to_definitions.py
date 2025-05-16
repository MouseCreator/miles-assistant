from typing import List

from src.miles.core.plugin.plugin_definition import PluginDefinition, NamespaceOfCommands, StoredCommand
from src.miles.shared.priority.dynamic_priority import DynamicPriorityRuleSet
from src.miles.core.priority.priority_manager import PriorityManager
from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet
from src.miles.shared.register import MilesRegister, PluginRegister, NamespaceInitializer
from src.miles.utils.singleton import Singleton


def _build_priority_manager(namespace: NamespaceInitializer) -> PriorityManager:
    priority_manager = PriorityManager(default_priority=namespace.get_default_priority(), strategy=namespace.get_priority_strategy())
    rules = namespace.get_static_priorities()
    for rule in rules:
        priority_manager.set_rule(rule)
    return priority_manager

def _map_matchings(namespace: NamespaceInitializer) -> MatchingDefinitionSet:
    matchings = namespace.get_matchings()
    definition_set = MatchingDefinitionSet()
    definition_set.append_all_definitions(matchings)
    return definition_set

def _map_commands(namespace: NamespaceInitializer) -> List[StoredCommand]:
    result = []
    for command in namespace.get_commands():
        result.append(
            StoredCommand(
                command.name,
                command.syntax,
                command.executor
            )
        )
    return result


def _map_dynamic_rules(namespace: NamespaceInitializer):
    rules = namespace.get_dynamic_priorities()
    dynamic_ruleset = DynamicPriorityRuleSet()
    dynamic_ruleset.extend(rules)
    return dynamic_ruleset


def _map_namespace(namespace: NamespaceInitializer) -> NamespaceOfCommands:
    name = namespace.get_name()
    prefix = namespace.get_prefix()
    definition_set = _map_matchings(namespace)
    commands = _map_commands(namespace)

    priority_manager = _build_priority_manager(namespace)

    dynamic_ruleset = _map_dynamic_rules(namespace)
    word_analyzer_factory = namespace.get_word_analyzer_factory()

    return NamespaceOfCommands(
        name=name,
        prefix=prefix,
        priority_manager=priority_manager,
        commands=commands,
        definition_set=definition_set,
        dynamic_priorities=dynamic_ruleset,
        word_analyzer_factory=word_analyzer_factory
    )

def _map_plugin(plugin: PluginRegister) -> PluginDefinition:
    name = plugin.get_name()
    display_name = plugin.get_display_name()

    namespaces = list(map(_map_namespace, plugin.get_namespaces()))

    return PluginDefinition(name, namespaces, display_name)

def map_register_to_definition(register: MilesRegister) -> List[PluginDefinition]:
    plugins = register.all_plugins()
    return list(map(_map_plugin, plugins))