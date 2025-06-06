from enum import Enum
from typing import List, Self, Any, TypeVar, Type, cast

from src.miles.shared.context.flags import Flags


class NodeType(Enum):
    WORD = 0
    MATCHING = 1
    OPTIONAL = 2
    LIST = 3
    CHOICE = 4
    ITEM = 5


T = TypeVar('T')


class CommandNode:
    _id: int
    _node_type: NodeType
    _name: str | None
    _children: List[Self]
    _value: List[str]
    _parent: Self | None
    _number: int | None
    _result: Any

    def __init__(self,
                 identity: int,
                 node_type: NodeType,
                 value: List[str] | None,
                 parent: None | Self = None,
                 name: None | str = None,
                 children: None | List[Self] = None,
                 number: None | int = None,
                 argument: None | str = None,
                 result: Any = None
                 ):
        self._argument = argument
        self._number = number
        self._id = identity
        self._node_type = node_type
        self._value = value
        self._name = name
        self._parent = parent
        self._result = result
        if children is None:
            self._children = []
        else:
            self._children = list(children)

    def __str__(self):
        return (
            f"CommandNode(id={self._id}, "
            f"type={self._node_type}, "
            f"name={self._name}, "
            f"value={self._value}, "
            f"number={self._number}, "
            f"children_count={len(self._children)})"
            f"argument={self._argument})"
            f"result={self._result})"
        )

    def __eq__(self, other):
        if not isinstance(other, CommandNode):
            return False
        return self._id == other._id

    def __iter__(self):
        return self._children.__iter__()

    def __bool__(self):
        return len(self._children) > 0

    def __len__(self):
        return len(self._children)

    def __getitem__(self, item):
        return self._children.__getitem__(item)

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

    def is_empty(self):
        return not self._children

    def number(self) -> int | None:
        return self._number

    def argument(self):
        return self._argument

    def append(self, struct: Self):
        self._children.append(struct)

    def set_argument(self, argument: str) -> None:
        self._argument = argument

    def any(self):
        return self.value()[0]

    def size(self):
        return len(self._children)

    def result(self) -> Any:
        if self._result is not None:
            return self._result
        if self._children:
            res = []
            for c in self._children:
                res.append(c.result())
            return res
        if len(self._value) == 0:
            return None
        if len(self._value) == 1:
            return self._value
        return list(self._value)

    def raw_result(self) -> Any:
        return self._result

    def results(self) -> List[Any]:
        result_list = []
        for ch in self.children():
            ch_res = ch.result()
            result_list.append(ch_res)
        return result_list

    def typed_result(self, expected_type: Type[T]) -> T:
        if isinstance(self._result, expected_type):
            return cast(T, self._result)
        else:
            raise TypeError(f"Expected result of type {expected_type.__name__}, "
                            f"but got {type(self._result).__name__}")


class NamespaceStructure:
    def __init__(self, identifier: str, tokens: List[str]):
        self._tokens = tokens
        self._identifier = identifier

    def identifier(self) -> str:
        return self._identifier

    def empty(self):
        return self.size() == 0

    def __len__(self):
        return self.size()

    def size(self):
        return len(self._tokens)

    def tokens(self):
        return list(self._tokens)


class CommandStructure:
    def __init__(self,
                 root_node: CommandNode,
                 tokens: List[str],
                 command_name: str,
                 namespace_structure: NamespaceStructure,
                 flags: Flags):
        self._root_node = root_node
        self._input = tokens
        self._command_name = command_name
        self._namespace_structure = namespace_structure
        self._flags = flags

    def get_root(self) -> CommandNode:
        return self._root_node

    def get_input(self) -> List[str]:
        return self._input

    def size(self):
        return len(self._input)

    def get_command_name(self) -> str:
        return self._command_name

    def has_namespace(self) -> bool:
        return not self._namespace_structure.empty()

    def namespace(self) -> NamespaceStructure:
        return self._namespace_structure

    def flags(self) -> Flags:
        return self._flags

    def results(self) -> List[Any]:
        return self._root_node.results()
