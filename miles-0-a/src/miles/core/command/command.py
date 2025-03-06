
from abc import ABC, abstractmethod
from enum import Enum


class ComponentType(Enum):

    # NAMESPACE : WORD WORD WORD {OPTIONAL} [LIST] matching (ONE_OF, ONE_OF, ONE_OF)
    # <<group1>> : <<group2>> <<group3>> <<group4>>
    NAMESPACE = 1 # specifies the command's scope
    WORD = 2 # reserved word
    OPTIONAL = 3 # optional group: repeat 0 or 1 times
    LIST = 4 # list of components: repeat 1 or more times
    MATCHING = 5 # special group
    ONE_OF = 6 # list of options, expects to match 1 and only 1 word from the given list
    GROUP = 7 # aggregates multiple components, automatically generated


class CommandComponent(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass
    @abstractmethod
    def get_priority(self) -> int:
        pass
    @abstractmethod
    def get_type(self) -> ComponentType:
        pass

class Command:
    def __init__(self):
        pass