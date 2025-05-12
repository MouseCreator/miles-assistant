from typing import List

from src.miles.core.matcher.matcher import ConnectionType
from src.miles.core.normalized.history import NorHistory
from src.miles.core.processor.command_structure import CommandStructure


class _ProtoNode:
    def __init__(self, name, p_type, children):
        pass

class _ProtoNodeStack:
    def __init__(self):
        pass

class StructFactory:

    def __init__(self):
        pass

    def _process_labels(self, label: str):
        pass

    def convert(self, tokens: List[str], history: NorHistory) -> CommandStructure:
        items = history.all_items()
        stack = _ProtoNodeStack()
        for item in items:
            conn = item.connection
            if conn.connection_type == ConnectionType.AUTOMATIC:
                label: str = conn.connection_arg

                if label == 'begin name':
                    pass
                elif label == 'end name':
                    pass
                elif label == 'begin list':
                    pass
                elif label == 'begin optional':
                    pass
                elif label == 'skip optional':
                    pass

            else:
                pass

