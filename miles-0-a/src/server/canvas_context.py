from typing import List


class Shape:
    def __init__(self, identity: int, category: str, x: int, y: int, color: str, angle: int):
        self.identity = identity
        self.category = category
        self.x = x
        self.y = y
        self.color = color
        self.angle = angle

    def to_dict(self):
        return {
            "identity": self.identity,
            "category": self.category,
            "x": self.x,
            "y": self.y,
            "color": self.color,
            "angle": self.angle
        }

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

    def add(self, shape: Shape) -> None:
        self._list.append(shape)


class RequestContext:
    def __init__(self, shapes: List[Shape], identity_count: int):
        self._shapes = ShapeList(shapes)
        self._id_count = identity_count
    def shapes(self) -> ShapeList:
        return self._shapes

    def new_identity(self) -> int:
        self._id_count += 1
        return self._id_count

    def clear_identity(self):
        self._id_count = 0

    def identity(self):
        return self._id_count
