from enum import Enum


class RecOptimizationStrategy(Enum):
    """
    Optimization strategies define behavior of context analyzer in case there are multiple exits from the node;
    Shortest first strategy assumes that the shortest recognized sequence is correct and must be processed before others.
    Longest first strategy assumes that the longest recognized sequence is correct and must be processed before others.

    For example, we are provided with a context analyzer consumes that matches only the 'a' symbol.
    Input string is "a a a b".
    Shortest first strategy will generate 3 pointers: ["a", "a a", "a a a"]
    Longest first strategy will also generate 3 pointers, but in different order: ["a a a", "a a", "a"]

    None strategy will process the pointers in order they are recognized, usually leading to shortest first.
    Randomize strategy will shuffle the pointers, so the output like ["a a", "a", "a a a"] is possible.
    """
    NONE = 0,
    SHORTEST_FIRST = 1,
    LONGEST_FIRST = 2,
    RANDOMIZE = 3
