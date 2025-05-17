
from collections import Counter
from typing import List



def compare_words(target: str, actual: str) -> float:
    if target == actual:
        return 100
    t_size = len(target)
    if len(target) != len(actual) or t_size < 3:
        return 0

    swap_groups1 = []
    swap_groups2 = []
    is_swapping = False
    current_group1 = ''
    current_group2 = ''
    correct_chars = 0
    for i in range(t_size):
        ch1 = target[i]
        ch2 = actual[i]
        if not is_swapping:
            if ch1 == ch2:
                correct_chars += 1
                continue
            is_swapping = True
            current_group1 = ch1
            current_group2 = ch2
        else:
            if ch1 == ch2:
                is_swapping = False
                swap_groups1.append(current_group1)
                swap_groups2.append(current_group2)
                current_group1 = ''
                current_group2 = ''
                correct_chars += 1
            else:
                current_group1 += ch1
                current_group2 += ch2
    for g1, g2 in zip(swap_groups1, swap_groups2):
        if len(g1) > 3:
            return 0
        if Counter(g1) != Counter(g2):
            return 0

    return 100 * correct_chars / t_size

def is_one_of(current_word: str, group: List[str]) -> (str | None, float):
    max_certainty = 0
    closest = None
    for candidate in group:
        certainty = compare_words(current_word, candidate)
        if certainty > max_certainty:
            max_certainty = certainty
            closest = candidate
    return closest, max_certainty


