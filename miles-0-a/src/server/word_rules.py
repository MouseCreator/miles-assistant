from typing import List

from src.server.sounds import sound_similarity, find_closest_sounding_word
from src.server.typos import compare_words, is_one_of


def rule_is_equal_words(word1: str, word2: str, origin: str) -> float:
    w1 = word1.lower()
    w2 = word2.lower()
    if origin == 'text':
        return compare_words(w1, w2)
    elif origin == 'audio':
        if sound_similarity(w1, w2) == 0:
            return 100
    return 0

def rule_is_one_of(word: str, arr: List[str], origin: str) -> (str | None, float):
    word = word.lower()
    if origin == 'text':
        return is_one_of(word, arr)
    elif origin == 'audio':
        closest, distance = find_closest_sounding_word(word, arr)
        if distance == 0:
            return closest, 100
    return None, 0
