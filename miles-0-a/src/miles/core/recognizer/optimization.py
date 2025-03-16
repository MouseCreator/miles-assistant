from enum import Enum


class RecOptimizationStrategy(Enum):
    NONE = 0,
    SHORTEST_FIRST = 1,
    LONGEST_FIRST = 2,
    RANDOMIZE = 3


# SoundOptimizationStrategy(Enum):