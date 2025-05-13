from src.miles.core.matching_core import MatchingCore
from src.miles.core.plugin.pipeline import create_normalized_matcher_from_definitions, \
    create_normalized_matcher_for_namespaces
from src.miles.core.plugin.register_to_definitions import map_register_to_definition
from src.miles.core.register.register import MilesRegister


def collect_plugins():
    pass

def create_matching_core() -> MatchingCore:
    collect_plugins()
    register = MilesRegister()
    definitions = map_register_to_definition(register)
    namespace_matcher = create_normalized_matcher_for_namespaces(definitions)
    plugin_structures = list(map(create_normalized_matcher_from_definitions, definitions))

    return MatchingCore(namespace_matcher=namespace_matcher, plugin_structures=plugin_structures)

