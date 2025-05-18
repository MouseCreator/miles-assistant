from src.miles.utils.singleton import Singleton


class IdGenerator(metaclass=Singleton):
    def __init__(self):
        self._current = 1
        self._context_map = {}

    def next(self, context) -> int:
        if context not in self._context_map:
            self._context_map[context] = 1
        result = self._context_map[context]
        self._context_map[context] = result + 1
        return result

    def next_global(self):
        result = self._current
        self._current += 1
        return result
