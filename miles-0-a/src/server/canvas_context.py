from typing import List


class Shape:
    def __init__(self, identity: str, category: str, x: int, y: int, color: str, angle: int):
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

    def get_by_id(self, identifier: str) -> Shape | None:
        for s in self._list:
            if s.identity.lower() == identifier.lower():
                return s
        return None

    def remove_by_id(self, target: str):
        self._list = [el for el in self._list if el.identity.lower() != target.lower()]

    def clear(self):
        self._list = []

    def size(self):
        return len(self._list)

    def __len__(self):
        return len(self._list)

    def add(self, shape: Shape) -> None:
        self._list.append(shape)


def _next_shape_id(number: int) -> str:
    if number < 1:
        raise ValueError("Number of a shape must be greater than or equal to 1")
    number -= 1
    base = 26
    letter = chr(ord('A') + (number % base))
    suffix = number // base

    return letter if suffix == 0 else f"{letter}{suffix - 1}"


class RequestContext:
    def __init__(self, shapes: List[Shape], identity_count: int):
        self._shapes = ShapeList(shapes)
        self._id_count = identity_count
        self._recognized = ''

    def shapes(self) -> ShapeList:
        return self._shapes

    def set_recognized(self, command: str):
        self._recognized = command

    def get_recognized(self) -> str:
        return self._recognized

    def new_identity(self) -> str:
        self._id_count += 1
        return _next_shape_id(self._id_count)

    def clear_identity(self):
        self._id_count = 0

    def identity(self):
        return self._id_count
