from typing import List


def decapitalize(s: str) -> str:
    if s and s[0].isupper():
        return s[0].lower() + s[1:]
    return s


def print_list(lst: List, separator=', ') -> str:
    return "[" + separator.join(map(str, lst)) + "]"
