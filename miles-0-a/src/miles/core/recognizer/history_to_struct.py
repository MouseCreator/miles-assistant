from typing import List
import re

from src.miles.core.normalized.history import NorHistory
from src.miles.core.processor.command_structure import CommandNode, NodeType
from src.miles.core.recognizer.normalized_matcher import HistoryNodeType
from src.miles.utils.id_generator import IdGenerator


class _ProtoNode:
    def __init__(self, name, p_type, children):
        pass

class _ProtoNodeStack:
    def __init__(self):
        pass

class StructFactory:

    def __init__(self):
        self.id_generator = IdGenerator()

    def _process_labels(self, label: str):
        pass


    def _next_index(self):
        return self.id_generator.next('command_node')

    def _extract_option_value(self, input_string):
        match = re.fullmatch(r'option\s+(\d+)', input_string)
        if match:
            return int(match.group(1))
        else:
            raise ValueError(f"Incorrect format of choice option: {input_string}")

    def _convert(self, tokens: List[str], history: NorHistory) -> CommandNode:
        items = history.all_items()
        stack = [ CommandNode(
            identity=self._next_index(),
            node_type=NodeType.ITEM,
            value=None,
        ) ]
        item_queue = list(items)

        while item_queue:
            item = item_queue.pop(0)
            node = item.node
            parent=stack[0]
            if node.node_type == HistoryNodeType.AUTOMATIC:
                label: str = node.argument
                if label == 'skip optional':
                    struct = CommandNode(
                        identity=self._next_index(),
                        node_type=NodeType.OPTIONAL,
                        value=None,
                        name=node.name,
                        children=[],
                        parent=parent,
                        number=0
                    )
                    parent.append(struct)
                elif label == 'begin optional':
                    struct = CommandNode(
                        identity=self._next_index(),
                        node_type=NodeType.OPTIONAL,
                        value=None,
                        name=node.name,
                        children=[],
                        parent=parent,
                        number=1
                    )
                    parent.append(struct)
                    stack.insert(0, struct)
                elif label == 'end optional':
                    stack.pop(0)
                elif label == 'begin list':
                    list_struct = CommandNode(
                        identity=self._next_index(),
                        node_type=NodeType.LIST,
                        value=None,
                        name=node.name,
                        children=[],
                        parent=parent
                    )
                    parent.append(list_struct)
                    stack.insert(0, list_struct)
                    stack.insert(0, CommandNode(
                        identity=self._next_index(),
                        node_type=NodeType.ITEM,
                        value=None,
                        name=node.name,
                        children=[],
                        parent=list_struct,
                        number=0
                    ))
                elif label == 'repeat list':
                    stack.pop(0) # pop previous item
                    list_struct = stack[0]
                    stack.insert(0, CommandNode( # begin new item
                        identity=self._next_index(),
                        node_type=NodeType.ITEM,
                        value=None,
                        name=node.name,
                        children=[],
                        parent=list_struct,
                        number=len(list_struct)
                    ))
                elif label == 'end list':
                    stack.pop(0) # pops item node
                    stack.pop(0) # pops list node
                elif label == 'begin choice':
                    if not item_queue:
                        raise ValueError(f'Expected to have choice option selected, but got end of input')

                    choice_number_item = item_queue.pop(0)
                    number_argument = choice_number_item.node.argument
                    number = self._extract_option_value(number_argument)
                    struct = CommandNode(
                        identity=self._next_index(),
                        node_type=NodeType.CHOICE,
                        value=None,
                        name=node.name,
                        children=[],
                        parent=parent,
                        number=number
                    )
                    parent.append(struct)
                    stack.insert(0, struct)
                elif label == 'end choice':
                    stack.pop(0)


            elif node.node_type == HistoryNodeType.MATCHING:
                word: str = node.argument

        if len(stack) != 1:
            raise ValueError(f'Invalid stack state: {stack}')
        return stack[0]

    def convert(self, has_namespace: bool, tokens: List[str], history: NorHistory):
        root_node = self._convert(tokens, history)



