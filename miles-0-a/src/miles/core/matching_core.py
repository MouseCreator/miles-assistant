from typing import List, Tuple

from src.miles.core.context.data_holder import TextDataHolder
from src.miles.core.plugin.plugin_structure import PluginStructure
from src.miles.core.recognizer.analyzer_provider import AnalyzerProvider
from src.miles.core.recognizer.history_to_struct import StructFactory
from src.miles.core.recognizer.normalized_matcher import NormalizedMatcher
from src.miles.core.recognizer.normalized_text_recognizer import TextRecognizer
from src.miles.core.tokenizer import Tokenizer



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
        self._analyzer_provider = AnalyzerProvider(self._plugin_structures[0].)
        self._tokenizer = Tokenizer()


    def recognize_and_process(self, command: str, namespace: str | None):
        tokens = self._tokenize(command)
        shift = 0
        if namespace is None:
            namespace, shift = self._match_namespace(tokens)

    def _tokenize(self, command: str) -> List[str]:
        return self._tokenizer.tokenize(command)

    def _match_namespace(self, tokens: List[str]) -> Tuple[str, int]:
        data_holder = TextDataHolder(tokens)
        recognizer = TextRecognizer(
            self._namespace_matcher, data_holder
        )

        recognizer.recognize()

