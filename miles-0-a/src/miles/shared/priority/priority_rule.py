from abc import abstractmethod, ABC
from enum import Enum


class RuleType(Enum):
    GENERAL_WORD = 0,
    GENERAL_MATCHING = 1,
    GENERAL_AUTOMATIC = 2
    SPECIFIC_WORD = 3,
    SPECIFIC_MATCHING = 4,
    SPECIFIC_AUTOMATIC = 5,
    NAMED = 6


class PriorityRule(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_priority(self, argument: str) -> int | None:
        """
        Calculates priority based on the argument
        :return: priority if the rule can define priority for the given argument, otherwise None
        """
        pass

    @abstractmethod
    def rule_type(self) -> RuleType:
        pass

    def arg(self) -> None | str:
        return None


class GeneralWordRule(PriorityRule):

    def __init__(self, priority: int):
        super().__init__()
        self.priority = priority

    def rule_type(self) -> RuleType:
        return RuleType.GENERAL_WORD

    def get_priority(self, argument: str) -> int:
        return self.priority


class GeneralMatchingRule(PriorityRule, ABC):

    def __init__(self, priority: int):
        super().__init__()
        self.priority = priority

    def rule_type(self) -> RuleType:
        return RuleType.GENERAL_MATCHING

    def get_priority(self, argument: str) -> int:
        return self.priority


class GeneralAutomaticRule(PriorityRule, ABC):

    def __init__(self, priority: int):
        super().__init__()
        self.priority = priority

    def rule_type(self) -> RuleType:
        return RuleType.GENERAL_MATCHING

    def get_priority(self, argument: str) -> int:
        return self.priority


class ConstructedRule(PriorityRule, ABC):
    def __init__(self, argument: str, priority: int):
        super().__init__()
        self.argument = argument
        self.priority = priority

    def get_priority(self, argument: str) -> int:
        return self.priority

    @abstractmethod
    def rule_type(self) -> RuleType:
        pass

    def arg(self) -> None | str:
        return self.argument


class NamedRule(PriorityRule, ABC):
    def __init__(self, of_word: str, priority: int):
        super().__init__(of_word, priority)

    def rule_type(self) -> RuleType:
        return RuleType.NAMED


class SpecificWordRule(ConstructedRule):
    def __init__(self, of_word: str, priority: int):
        super().__init__(of_word, priority)

    def rule_type(self) -> RuleType:
        return RuleType.SPECIFIC_WORD


class SpecificMatchingRule(ConstructedRule):
    def __init__(self, of_word: str, priority: int):
        super().__init__(of_word, priority)

    def rule_type(self) -> RuleType:
        return RuleType.SPECIFIC_MATCHING


class AutomaticRule(ConstructedRule):
    def __init__(self, of_word: str, priority: int):
        super().__init__(of_word, priority)

    def rule_type(self) -> RuleType:
        return RuleType.SPECIFIC_AUTOMATIC
