from typing import List


def index_of(lst: List, element) -> int:
    for i in range(len(lst)):
        e = lst[i]
        if e == element:
            return i
    return -1
