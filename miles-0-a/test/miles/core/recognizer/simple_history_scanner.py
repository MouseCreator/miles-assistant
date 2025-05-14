from typing import List

from src.miles.core.matcher.matcher import ConnectionType
from src.miles.core.recognizer.recognizer_pointer import RecPointer


def scan_history(text: str, reached_pointer: RecPointer) -> List[str]:
    tokens = text.split(' ')
    history = reached_pointer.get_history()
    items = history.all_items()
    result = []
    for item in items:
        if item.connection.connection_type == ConnectionType.AUTOMATIC:
            result.append('!' + item.connection.connection_arg)
        else:
            from_i = item.prev_point
            to_i = item.next_point
            sb = []
            for i in range(from_i, to_i):
                if i in item.included:
                    sb.append(tokens[i])
            result.append(' '.join(sb))
    return result


