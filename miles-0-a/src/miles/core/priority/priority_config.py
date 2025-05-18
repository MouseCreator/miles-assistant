from enum import Enum


class PriorityStrategy(Enum):
    FIRST = 0
    FIND_MAX = 1
    ALL_DEFAULT = 2


class PriorityConfig:
    def get_strategy(self) -> PriorityStrategy:
        pass

    def get_rules(self):
        pass

    def get_named(self):
        pass

    def get_nodes(self):
        pass
