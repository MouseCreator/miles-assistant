from enum import Enum
from typing import List, Self


class NodeType(Enum):
    WORD = 0
    MATCHING = 1
    OPTIONAL = 2
    LIST = 3
    CHOICE = 4


class CommandNode:
    _id: int
    _node_type: NodeType
    _name: str | None
    _children: List[Self]
    _value: str
    _option_num: None | int
    _parent: Self | None
    def __init__(self,
                 identity: int,
                 node_type: NodeType,
                 value: str,
                 parent: None | Self = None,
                 name: None | str = None,
                 children: None | List[Self] = None
                 ):
        self._id = identity
        self._node_type = node_type
        self._value = value
        self._name = name
        self._parent = parent
        if children is None:
            self._children = []
        else:
            self._children = list(children)

    def __eq__(self, other):
        if not isinstance(other, CommandNode):
            return False
        return self._id == other._id
    def __iter__(self):
        return self._children.__iter__()

    def has_parent(self) -> bool:
        return self._parent is not None
    def children(self) -> List[Self]:
        return list(self._children)
    def name(self):
        return self._name
    def value(self):
        return self._value
    def parent(self):
        return self._parent
    def node_type(self):
        return self._node_type


class CommandStructure:
    def __init__(self,
                 root_node: CommandNode,
                 input_string: str,
                 command_name: str,
                 command_syntax: str):
        self._root_node = root_node
        self._input = input_string
        self._command_name = command_name
        self._command_syntax = command_syntax

    def get_root(self) -> CommandNode:
        return self._root_node

    def get_input(self) -> str:
        return self._input

    def get_command_name(self) -> str:
        return self._command_name

    def get_command_syntax(self) -> str:
        return self._command_syntax