from typing import List

from src.miles.core.command.generic_command_processor import GenericCommandProcessor

from src.miles.core.matcher.matcher_factory import MatcherFactory
from src.miles.core.normalized.matcher_normalizer import normalize
from src.miles.core.plugin.plugin_definition import PluginDefinition
from src.miles.core.plugin.plugin_structure import PluginStructure, NamespaceComponent
from src.miles.core.recognizer.priority_assign import PriorityAssigner


def create_normalized_matcher_from_command_string(plugin_definition: PluginDefinition) -> PluginStructure:

    plugin_name = plugin_definition.name()
    priority_manager = plugin_definition.get_priority_manager()
    priority_assigner = PriorityAssigner(priority_manager)
    match_factory = MatcherFactory()
    namespace_components: List[NamespaceComponent] = []
    for namespace in plugin_definition._namespaces:
        namespace_matcher = match_factory.create_namespace(namespace)
        matcher = match_factory.empty_matcher()
        for stored_command in namespace.commands:
            command = GenericCommandProcessor().process(stored_command.name)
            match_factory.add_command(matcher, command, stored_command.name)
        normalized_matcher = normalize(matcher)
        normalized_namespace_matcher = normalize(namespace_matcher)
        priority_assigner.assign_all(plugin_name, normalized_matcher)

        namespace_component = NamespaceComponent(namespace.name, normalized_namespace_matcher, normalized_matcher)
        namespace_components.append(namespace_component)

    return PluginStructure(plugin_name, namespace_components, definitions=plugin_definition.definition_set())




