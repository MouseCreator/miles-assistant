from src.miles.core.priority.priority_config import PriorityStrategy

from typing import Dict, Tuple

from src.miles.core.priority.priority_rule import PriorityRule, RuleType
from src.miles.core.recognizer.normalized_matcher import HistoryNodeType, NormalizedNode


class PriorityManager:

    _def_priority: int
    _strategy: PriorityStrategy
    _named_priorities: Dict[Tuple[str, str], int]
    _node_priorities: Dict[Tuple[str, HistoryNodeType, str], int]

    def __init__(self, strategy: PriorityStrategy = PriorityStrategy.FIND_MAX, default_priority = 0):
        self._node_priorities = {}
        self._named_priorities = {}
        self._strategy = strategy
        self._def_priority = default_priority
        self._def_word = default_priority
        self._def_matching = default_priority
        self._def_automatic = default_priority

    def get_strategy(self):
        return self._strategy

    def get_priority(self, plugin: str, node : NormalizedNode) -> int:

        default_priority =  self.default_priority()

        if node.node_type == HistoryNodeType.WORD:
            default_priority = self._def_word
        elif node.node_type == HistoryNodeType.MATCHING:
            default_priority = self._def_matching
        elif node.node_type == HistoryNodeType.AUTOMATIC:
            default_priority = self._def_automatic

        node_key = (plugin, node.node_type, node.argument)
        priority1 = self._node_priorities.get(node_key, None)

        named_key = (plugin, node.name)
        priority2 = self._named_priorities.get(named_key, None)

        if not priority1 and priority2:
            return default_priority
        if priority1 and priority2:
            return max(priority1, priority2)
        if priority1:
            return priority1
        if priority2:
            return priority2
        raise ValueError()

    def set_rule(self, rule: PriorityRule):
        if rule.rule_type()==RuleType.GENERAL_WORD:
            self._def_word = rule.get_priority('word')
        elif rule.rule_type()==RuleType.GENERAL_AUTOMATIC:
            self._def_automatic = rule.get_priority('automatic')
        elif rule.rule_type()==RuleType.GENERAL_MATCHING:
            self._def_matching = rule.get_priority('matching')
        elif rule.rule_type()==RuleType.SPECIFIC_WORD:
            self.set_word_priority(rule.plugin(), rule.arg(), rule.get_priority(''))
        elif rule.rule_type()==RuleType.SPECIFIC_AUTOMATIC:
            self.set_automatic_priority(rule.plugin(), rule.arg(), rule.get_priority(''))
        elif rule.rule_type()==RuleType.SPECIFIC_MATCHING:
            self.set_matching_priority(rule.plugin(), rule.arg(), rule.get_priority(''))
        elif rule.rule_type()==RuleType.NAMED:
            self.set_named_priority(rule.plugin(), rule.arg(), rule.get_priority(''))
        else:
            raise ValueError(f'Unknown rule type found in rule {rule}')

    def set_word_priority(self, plugin: str, word: str, priority: int):
        node_key = (plugin, HistoryNodeType.WORD, word)
        self._node_priorities[node_key] = priority

    def set_matching_priority(self, plugin: str, matching: str, priority: int):
        node_key = (plugin, HistoryNodeType.MATCHING, matching)
        self._node_priorities[node_key] = priority

    def set_automatic_priority(self, plugin: str, label: str, priority: int):
        node_key = (plugin, HistoryNodeType.AUTOMATIC, label)
        self._node_priorities[node_key] = priority

    def set_named_priority(self, plugin: str, named: str, priority: int):
        named_key = (plugin, named)
        self._named_priorities[named_key] = priority

    def default_priority(self):
        return self._def_priority
