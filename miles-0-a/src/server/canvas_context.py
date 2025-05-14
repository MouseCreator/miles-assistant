from typing import List


class Shape:
    def __init__(self, identity: int, category: str, x: int, y: int, color: str, angle: int):
        self.identity = identity
        self.category = category
        self.x = x
        self.y = y
        self.color = color
        self.angle = angle

class ShapeList:
    def __init__(self, lst: List[Shape]):
        self._list = lst

    def __iter__(self):
        return iter(self._list)

    def get_by_id(self, number: int) -> Shape | None:
        for s in self._list:
            if s.identity == number:
                return s
        return None

    def remove_by_id(self, target: int):
        self._list = [el for el in self._list if el.identity != target]

    def clear(self):
        self._list = []


class RequestContext:
    def __init__(self, shapes: List[Shape]):
        self._shapes = ShapeList(shapes)
    def shapes(self) -> ShapeList:
        return self._shapes