from abc import ABC
from enum import Enum
from typing import Self, List


class ComponentType(Enum):

    # NAMESPACE : WORD WORD WORD {OPTIONAL} [LIST] matching (ONE_OF, ONE_OF, ONE_OF)
    # <<group1>> : <<group2>> <<group3>> <<group4>>
    ROOT = 0
    WORD = 1 # reserved word
    OPTIONAL = 2 # optional group: repeat 0 or 1 times
    LIST = 3 # list of components: repeat 1 or more times
    MATCHING = 4 # special group
    CHOICE = 5 # list of options, expects to match 1 and only 1 word from the given list
    SEQUENCE = 6


class CommandComponent(ABC):

    def get_priority(self) -> int:
        pass

    def get_type(self) -> ComponentType:
        pass

    def get_content(self) -> str | Self | List[Self]:
        return None

    def __str__(self):
        content = self.get_content()
        if isinstance(content, List):
            t = ','.join(str(x) for x in content)
            return f'({self.get_type().name}, {t})'
        else:
            return f'({self.get_type().name}, {content})'

class SequenceComponent(CommandComponent):
    def __init__(self, sequence: List[CommandComponent]):
        self._content = sequence
    def get_type(self) -> ComponentType:
        return ComponentType.SEQUENCE
    def get_content(self) -> List[CommandComponent]:
        return list(self._content)

class WordComponent(CommandComponent):
    def __init__(self, word: str):
        self._word = word
    def get_type(self) -> ComponentType:
        return ComponentType.WORD
    def get_content(self) -> str:
        return self._word

class MatchingComponent(CommandComponent):
    def __init__(self, matching_key: str):
        self._matching_key = matching_key
    def get_type(self) -> ComponentType:
        return ComponentType.MATCHING
    def get_content(self) -> str:
        return self._matching_key

class OptionalComponent(CommandComponent):
    def __init__(self, content: SequenceComponent):
        self._inner = content

    def get_type(self) -> ComponentType:
        return ComponentType.OPTIONAL
    def get_content(self) -> SequenceComponent:
        return self._inner

class RootComponent(CommandComponent):
    def __init__(self, content: CommandComponent):
        self._content = content
    def get_type(self) -> ComponentType:
        return ComponentType.ROOT
    def get_content(self) -> CommandComponent:
        return self._content

class ListComponent(CommandComponent):
    def __init__(self, content: List[SequenceComponent]):
        self._content = content
    def get_type(self) -> ComponentType:
        return ComponentType.LIST
    def get_content(self) -> List[SequenceComponent]:
        return list(self._content)

class ChoiceComponent(CommandComponent):
    def __init__(self, options: List[SequenceComponent]):
        self._options = options
    def get_type(self) -> ComponentType:
        return ComponentType.CHOICE
    def get_content(self) -> List[SequenceComponent]:
        return list(self._options)


class Command:
    def __init__(self, root: RootComponent):
        self.root = root
    def __str__(self):
        return f"Command: {self.root}"