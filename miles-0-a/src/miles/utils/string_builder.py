from typing import Self, List


class StringBuilder:
    def __init__(self):
        self._buffer = ''

    def append(self, any_object) -> Self:
        self._buffer += str(any_object)
        return self

    def append_optional(self, opt) -> Self:
        if opt is None:
            return self
        return self.append(opt)

    def to_string(self) -> str:
        return self._buffer

    def __str__(self):
        return self._buffer


def lines(lines_to_concat: List[str]) -> str:
    return "\n".join(lines_to_concat)
