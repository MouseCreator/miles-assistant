from typing import Self


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
