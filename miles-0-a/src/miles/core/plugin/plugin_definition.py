from typing import List

from src.miles.core.command.command import WordComponent
from src.miles.core.matcher.comand_defintion import CommandNamespace
from src.miles.shared.certainty import CertaintyEffect
from src.miles.shared.context_analyzer import WordContextAnalyzerFactory
from src.miles.shared.executor.command_executor import CommandExecutor
from src.miles.shared.priority.dynamic_priority import DynamicPriorityRuleSet
from src.miles.core.recognizer.matching_definition import MatchingDefinitionSet
from src.miles.core.priority.priority_manager import PriorityManager


class StoredCommand:
    def __init__(self, name: str, syntax: str, executor: CommandExecutor):
        self.name = name
        self.syntax = syntax
        self.executor = executor

class NamespaceOfCommands:
    def __init__(self,
                 name: str,
                 prefix: str | None,
                 commands: List[StoredCommand],
                 priority_manager: PriorityManager,
                 dynamic_priorities: DynamicPriorityRuleSet,
                 definition_set : MatchingDefinitionSet,
                 word_analyzer_factory: WordContextAnalyzerFactory,
                 certainty_effect: CertaintyEffect):
        self.name = name
        if prefix is None:
            prefix=''
        self.prefix = prefix
        self.commands = commands
        self.dynamic_priorities = dynamic_priorities
        self.priority_manager = priority_manager
        self.definition_set = definition_set
        self.word_analyzer_factory = word_analyzer_factory
        self.certainty_effect: CertaintyEffect = certainty_effect

    def as_command_namespace(self):
        words = self.prefix.split() if self.prefix.strip() else []
        components = []
        for word in words:
            components.append(WordComponent(word))
        return CommandNamespace(
            namespace_name=self.name,
            arguments=components
        )

class PluginDefinition:
    def __init__(self,
                 name: str,
                 namespaces: List[NamespaceOfCommands],
                 display: str|None = None):
        self._namespaces = namespaces
        self._name = name
        if display is None:
            display = self._name
        self._display_name = display

    def name(self):
        return self._name

    def namespaces(self) -> List[NamespaceOfCommands]:
        return list(self._namespaces)