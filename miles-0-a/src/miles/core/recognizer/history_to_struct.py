from typing import List
import re

from src.miles.core.normalized.history import NorHistory
from src.miles.core.executor.command_structure import CommandNode, NodeType, CommandStructure, NamespaceStructure
from src.miles.core.recognizer.normalized_matcher import HistoryNodeType
from src.miles.core.recognizer.recognizer_pointer import RecPointer
from src.miles.utils.id_generator import IdGenerator
from src.miles.utils.list_utils import get_elements_by_indexes


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

    def _extract_identifier(self, label: str):
        match = re.fullmatch(r"recognize\s+(\w+)", label.strip())
        if match:
            return match.group(1)
        raise ValueError(f'Cannot get command name from recognition label {label}')

    def _convert(self, tokens: List[str], history: NorHistory) -> CommandNode:
        items = history.all_items()
        root_node = CommandNode(
            identity=self._next_index(),
            node_type=NodeType.ITEM,
            value=None,
        )
        stack = [ root_node ]
        item_queue = list(items)

        while item_queue:
            item = item_queue.pop(0)
            node = item.node

            included_tokens = get_elements_by_indexes(tokens, item.included)

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
                elif self._is_recognition_label(label):
                    root_node.set_argument(self._extract_identifier(label))
                elif label == 'begin list':
                    list_struct = CommandNode(
                        identity=self._next_index(),
                        node_type=NodeType.LIST,
                        value=None,
                        name=node.name,
                        parent=parent
                    )
                    parent.append(list_struct)
                    stack.insert(0, list_struct)
                    stack.insert(0, CommandNode(
                        identity=self._next_index(),
                        node_type=NodeType.ITEM,
                        value=None,
                        name=node.name,
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
                        parent=parent,
                        number=number
                    )
                    parent.append(struct)
                    stack.insert(0, struct)
                elif label == 'end choice':
                    stack.pop(0)
                else:
                    raise ValueError(f'Invalid label: {label}')
            elif node.node_type == HistoryNodeType.WORD:
                struct = CommandNode(
                    identity=self._next_index(),
                    argument=node.argument,
                    node_type=NodeType.WORD,
                    value=included_tokens,
                    name=node.name,
                    parent=parent
                )
                parent.append(struct)
            elif node.node_type == HistoryNodeType.MATCHING:
                struct = CommandNode(
                    identity=self._next_index(),
                    argument=node.argument,
                    node_type=NodeType.MATCHING,
                    value=included_tokens,
                    name=node.name,
                    parent=parent
                )
                parent.append(struct)

        if len(stack) != 1:
            raise ValueError(f'Invalid stack state: {stack}')
        return stack[0]

    def convert_command(self,
                namespace_structure: NamespaceStructure,
                tokens: List[str],
                pointer: RecPointer,
                ) -> CommandStructure:
        history = pointer.get_history()
        pointer_flags = pointer.flags()
        root_node = self._convert(tokens, history)
        return CommandStructure(
            root_node=root_node,
            namespace_structure=namespace_structure,
            tokens=tokens,
            command_name=root_node.argument(),
            flags=pointer_flags
        )

    def _convert_namespace(self, tokens: List[str], history: NorHistory):
        items = history.all_items()
        item_queue = list(items)
        namespace_tokens = []
        namespace_id = None
        for item in item_queue:
            if item.node.node_type == HistoryNodeType.WORD:
                namespace_tokens.extend([tokens[i] for i in range(item.prev_point, item.next_point)])
            elif item.node.node_type == HistoryNodeType.AUTOMATIC:
                label = item.node.argument
                if self._is_recognition_label(label):
                    namespace_id = self._extract_identifier(label)
                else:
                    raise ValueError(f'Unexpected automatic item in the namespace: {item}')
            else:
                raise ValueError(f"Unexpected item in the namespace: {item}")
        return NamespaceStructure(
            tokens=namespace_tokens,
            identifier=namespace_id
        )

    def convert_namespace(self, tokens: List[str], pointer: RecPointer) -> NamespaceStructure:
        history = pointer.get_history()
        return self._convert_namespace(tokens, history)

    def _is_recognition_label(self, label) -> bool:
        if label is None:
            return False
        return label.startswith('recognize ')







