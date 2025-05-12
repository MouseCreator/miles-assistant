from enum import Enum
from typing import List, Self


class NodeType(Enum):
    WORD = 0
    MATCHING = 1
    OPTIONAL = 2
    LIST = 3
    CHOICE = 4

class RecognizerType(Enum):
    TEXT = 0
    VOICE = 1

class CommandNode:
    _id: int
    _node_type: NodeType
    _name: str | None
    _children: List[Self]
    _value: str
    def __init__(self,
                 identity: int,
                 node_type: NodeType,
                 value: str,
                 name: None | str = None,
                 children: None | List[Self] = None):
        self._id = identity
        self._node_type = node_type
        self._value = value
        self._name = name
        if children is None:
            self._children = []
        else:
            self._children = list(children)


class CommandStructure:
    def __init__(self, root_node: CommandNode, recognizer: RecognizerType):
        self._root_node = root_node
        self._recognizer = recognizer

    def get_root(self) -> CommandNode:
        return self._root_node