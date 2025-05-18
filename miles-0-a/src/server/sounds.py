from typing import List

import Levenshtein
from metaphone import doublemetaphone


def sound_similarity(w1: str, w2: str) -> int:
    mp1 = doublemetaphone(w1)
    mp2 = doublemetaphone(w2)

    distances = []
    for code1 in mp1:
        for code2 in mp2:
            if code1 and code2:
                distances.append(Levenshtein.distance(code1, code2))
    return min(distances) if distances else 100


def find_closest_sounding_word(target: str, arr: List[str]) -> (str | None, float):
    closest = None
    min_distance = 100
    for word in arr:
        if word == target:
            return word, 0
        dist = sound_similarity(word, target)
        if dist < min_distance:
            min_distance = dist
            closest = word
    return closest, min_distance
