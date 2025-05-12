from typing import List, TypeVar


def index_of(lst: List, element) -> int:
    for i in range(len(lst)):
        e = lst[i]
        if e == element:
            return i
    return -1

T = TypeVar('T')

def get_elements_by_indexes(elements: List[T], indexes: List[int]) -> List[T]:
    if not indexes:
        return []
    try:
        return [elements[i - 1] for i in indexes]
    except IndexError:
        raise IndexError("One or more indexes are out of range.")