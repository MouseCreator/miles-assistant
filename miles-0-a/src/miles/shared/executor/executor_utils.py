from collections.abc import Callable
from typing import Generic, List, TypeVar



from src.miles.shared.executor.command_structure import CommandNode, NodeType

T = TypeVar('T')
class _ResultList(Generic[T]):
    def __init__(self):
        self._lst: List[T] = []

    def get(self) -> List[T]:
        return list(self._lst)

    def append(self, element: T) -> None:
        self._lst.append(element)

class CommandStructureSearch:
    def __init__(self, node: CommandNode):
        self._node = node

    def _find(self, current: CommandNode, predicate: Callable[[CommandNode], bool], result_list: _ResultList[CommandNode]) -> None:
        if current is None:
            return
        if predicate(current):
            result_list.append(current)
        for child in current.children():
            self._find(child, predicate, result_list)

    def find_all_named(self, target_name: str) -> List[CommandNode]:
        return self.find_all(lambda node: node.name() == target_name)

    def find_keyword(self, keyword: str) -> List[CommandNode]:
        keyword = keyword.upper()
        return self.find_all(lambda node: node.node_type() == NodeType.WORD and node.argument().upper() == keyword)

    def find_matching(self, matching: str) -> List[CommandNode]:
        matching = matching.upper()
        return self.find_all(lambda node: node.node_type() == NodeType.MATCHING and node.argument().upper() == matching)

    def find_by_type(self, of_type: NodeType) -> List[CommandNode]:
        return self.find_all(lambda node: node.node_type() == of_type)

    def find_all(self, predicate: Callable[[CommandNode], bool]):
        result_list = _ResultList()
        self._find(self._node, predicate, result_list)
        return result_list.get()