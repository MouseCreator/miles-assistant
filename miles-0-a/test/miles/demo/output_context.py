
class OutputContext:
    _output: str | None
    def __init__(self):
        self._output = None

    def set(self, item: str):
        self._output = item

    def get(self) -> str:
        return self._output