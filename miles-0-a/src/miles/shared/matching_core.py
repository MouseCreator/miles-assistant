from typing import List

from src.miles.core.core_context import CoreContext
from src.miles.core.plugin.plugin_structure import PluginStructure
from src.miles.shared.executor.command_structure import NamespaceStructure
from src.miles.core.recognizer.history_to_struct import StructFactory
from src.miles.core.recognizer.normalized_matcher import NormalizedMatcher
from src.miles.core.recognizer.normalized_text_recognizer import recognize_namespace, recognize_command
from src.miles.shared.tokenizer import Tokenizer



class MatchingCore:

    def __init__(self,
                 namespace_matcher: NormalizedMatcher,
                 plugin_structures: List[PluginStructure]):
        self._namespace_matcher = namespace_matcher
        self._namespace_name_map = {}
        for plugin in plugin_structures:
            for namespace in plugin.namespaces:
                name = namespace.name
                self._namespace_name_map[name] = (namespace, plugin)
        self._plugin_structures = list(plugin_structures)
        self._struct_factory = StructFactory()
        self._tokenizer = Tokenizer()


    def recognize_and_execute(self, command: str, core_context: CoreContext | None = None, namespace: str | None = None):
        tokens = self._tokenize(command)
        if core_context is None:
            core_context = CoreContext()
        if namespace is None:
            namespace_structure = recognize_namespace(self._namespace_matcher, tokens)
        else:
            namespace_structure = NamespaceStructure(identifier=namespace, tokens=[])

        namespace_id = namespace_structure.identifier()
        p_namespace, plugin = self._namespace_name_map[namespace_id]

        command_structure = recognize_command(p_namespace,
                                              tokens,
                                              namespace_structure)
        executor = p_namespace.executors_map.get(command_structure.get_command_name())
        executor.on_recognize(command_structure, core_context)


    def _tokenize(self, command: str) -> List[str]:
        return self._tokenizer.tokenize(command)


