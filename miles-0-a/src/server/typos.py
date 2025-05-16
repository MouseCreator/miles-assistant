
from collections import Counter
from typing import List


class TypoManager:

    def __init__(self):
        pass

    def compare_words(self, target: str, actual: str) -> float:
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

    def is_one_of(self, current_word: str, group: List[str]) -> float:
        max_certainty = 0
        for candidate in group:
            certainty = self.compare_words(current_word, candidate)
            max_certainty = max(certainty, max_certainty)
        return max_certainty


