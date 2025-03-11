from abc import ABC, abstractmethod
from enum import Enum
from typing import Self, List

from src.miles.utils.strings import decapitalize


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
        return 0
    @abstractmethod
    def get_type(self) -> ComponentType:
        pass

    @abstractmethod
    def get_content(self) -> str | Self | List[Self]:
        pass

    def __str__(self):
        content = self.get_content()
        if isinstance(content, List):
            t = ','.join(str(x) for x in content)
            return f'({self.get_type().name}:{t})'
        else:
            return f'({self.get_type().name}:{content})'
    @abstractmethod
    def accept_visitor(self, visitor):
        pass


class SequenceComponent(CommandComponent):
    def __init__(self, sequence: List[CommandComponent]):
        self._content = sequence
    def get_type(self) -> ComponentType:
        return ComponentType.SEQUENCE
    def get_content(self) -> List[CommandComponent]:
        return list(self._content)
    def accept_visitor(self, visitor):
        visitor.visit_sequence(self)

class WordComponent(CommandComponent):
    def __init__(self, word: str):
        self._word = word.upper()
    def get_type(self) -> ComponentType:
        return ComponentType.WORD
    def get_content(self) -> str:
        return self._word
    def accept_visitor(self, visitor):
        visitor.visit_word(self)

class MatchingComponent(CommandComponent):
    def __init__(self, matching_key: str):
        self._matching_key = decapitalize(matching_key)
    def get_type(self) -> ComponentType:
        return ComponentType.MATCHING
    def get_content(self) -> str:
        return self._matching_key

    def accept_visitor(self, visitor):
        visitor.visit_matching(self)

class OptionalComponent(CommandComponent):
    def __init__(self, content: SequenceComponent):
        self._inner = content

    def get_type(self) -> ComponentType:
        return ComponentType.OPTIONAL
    def get_content(self) -> SequenceComponent:
        return self._inner
    def accept_visitor(self, visitor):
        visitor.visit_optional(self)

class RootComponent(CommandComponent):
    def __init__(self, content: CommandComponent):
        self._content = content
    def get_type(self) -> ComponentType:
        return ComponentType.ROOT
    def get_content(self) -> CommandComponent:
        return self._content
    def accept_visitor(self, visitor):
        visitor.visit_root(self)

class ListComponent(CommandComponent):
    def __init__(self, content: SequenceComponent):
        self._content = content
    def get_type(self) -> ComponentType:
        return ComponentType.LIST
    def get_content(self) -> SequenceComponent:
        return self._content
    def accept_visitor(self, visitor):
        visitor.visit_list(self)

class NamedComponent(CommandComponent):
    def __init__(self, name: str, content: CommandComponent):
        self._name = name
        self._content = content
    def get_type(self) -> ComponentType:
        return ComponentType.CHOICE
    def get_content(self) -> CommandComponent:
        return self._content
    def get_name(self) -> str:
        return self._name
    def __str__(self):
        content = self.get_content()
        if isinstance(content, List):
            t = ','.join(str(x) for x in content)
        else:
            t = content
        return f'({self.get_name()}={t})'
    def accept_visitor(self, visitor):
        visitor.visit_named(self)


class ChoiceComponent(CommandComponent):
    def __init__(self, options: List[SequenceComponent]):
        self._options = options
    def get_type(self) -> ComponentType:
        return ComponentType.CHOICE
    def get_content(self) -> List[SequenceComponent]:
        return list(self._options)
    def accept_visitor(self, visitor):
        visitor.visit_choice(self)


class Command:
    def __init__(self, root: RootComponent):
        self.root = root
    def __str__(self):
        return f"Command: {self.root}"
    def accept_visitor(self, visitor):
        self.root.accept_visitor(visitor)

class ComponentVisitor(ABC):
    @abstractmethod
    def visit_root(self, root: RootComponent):
        pass

    @abstractmethod
    def visit_sequence(self, sequence: SequenceComponent):
        pass

    @abstractmethod
    def visit_word(self, word: WordComponent):
        pass

    @abstractmethod
    def visit_matching(self, matching: MatchingComponent):
        pass

    @abstractmethod
    def visit_optional(self, optional: OptionalComponent):
        pass

    @abstractmethod
    def visit_list(self, lst: ListComponent):
        pass

    @abstractmethod
    def visit_choice(self, choice: ChoiceComponent):
        pass

    @abstractmethod
    def visit_named(self, named: NamedComponent):
        pass