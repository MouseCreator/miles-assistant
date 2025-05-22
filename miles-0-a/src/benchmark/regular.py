import re
import time
from collections import Counter

import pandas as pd
from lark import Lark, Transformer
import matplotlib.pyplot as plt

from src.miles.shared.matching_core import MatchingCore
from src.miles.shared.matching_core_factory import create_matching_core
from src.miles.shared.register import MilesRegister
from test.miles.demo.test_errors import MockCommandExecutor

WORDS = ['apple', 'banana', 'orange', 'grape', 'pear']

def find_words_re(input_str, words):
    pattern = r'^(' + '|'.join(map(re.escape, words)) + r')( (' + '|'.join(map(re.escape, words)) + r'))*$'
    if re.fullmatch(pattern, input_str):
        return dict(Counter(input_str.split()))
    return {}

def build_lark_parser(words):
    word_alts = " | ".join(f'"{word}"' for word in words)
    grammar = f"""
        start: word (" " word)*

        word: {word_alts}
        %import common.WS
        %ignore WS
    """
    return Lark(grammar, parser='lalr')


def build_miles_parser(words):
    uppercase_words = [ u.upper() for u in words ]
    choice = ", ".join(uppercase_words)
    grammar = f"V [({choice})]"
    plugin = MilesRegister().create_plugin_register('benchmark')
    namespace_init = plugin.add_namespace("benchmark", "benchmark")
    namespace_init.add_command("words", grammar, MockCommandExecutor())
    result_core = create_matching_core()
    return result_core

def find_words_miles(input_str, m_core: MatchingCore):
    try:
        input_str = 'v ' + input_str
        m_core.recognize(input_str, namespace='benchmark')
        return dict(Counter(input_str.split()))
    except Exception:
        return {}

class WordCounter(Transformer):
    def start(self, items):
        return dict(Counter(items))

    def word(self, items):
        return str(items[0])


def find_words_lark(input_str, parser):
    try:
        tree = parser.parse(input_str)
        return WordCounter().transform(tree)
    except Exception:
        return {}


def select_index(i, n_words):
    return i % n_words


def benchmark(find_func, parser_provider, base_words, lengths):
    results_correct = []
    results_incorrect = []
    for length in lengths:
        input_words = []
        n_words = len(base_words)
        for i in range(length):
            random_index = select_index(i, n_words)
            input_words.append(base_words[random_index])
        input_str = " ".join(input_words)

        parser_or_words = parser_provider()
        start = time.time()
        find_func(input_str, parser_or_words)
        end = time.time()
        results_correct.append((end - start) * 1000)

        invalid_input_str = input_str + ' $$$'
        start = time.time()
        find_func(invalid_input_str, parser_or_words)
        end = time.time()
        results_incorrect.append((end - start) * 1000)

    return results_correct, results_incorrect

if __name__ == '__main__':
    base_words = list(WORDS)
    def re_provider():
        return WORDS
    def lark_provider():
        return build_lark_parser(WORDS)
    core = build_miles_parser(WORDS)
    def miles_provider():
        return core
    lengths = list(range(100, 5001, 100))
    result_miles_correct, results_miles_incorrect = benchmark(find_words_miles, miles_provider, base_words, lengths)
    print('Miles done!')
    results_re_correct, results_re_incorrect = benchmark(find_words_re, re_provider, base_words, lengths)
    print('RE done!')
    results_lark_correct, results_lark_incorrect = benchmark(find_words_lark, lark_provider, base_words, lengths)
    print('Lark done!')


    plt.figure()
    plt.plot(lengths, result_miles_correct, label='Correct Input', color='green')
    plt.plot(lengths, results_miles_incorrect, label='Incorrect Input', color='orangered')
    plt.xlabel("Input Size (Number of words in a string)")
    plt.ylabel("Time (ms)")
    plt.title("Miles: Benchmark")
    plt.legend()
    plt.grid(True)
    plt.show()

    data = {
        'Test Type': [
            'RE Correct', 'RE Incorrect',
            'Lark Correct', 'Lark Incorrect',
            'Miles Correct', 'Miles Incorrect'
        ],
    }

    for i, length in enumerate(lengths):
        data[f'Length {length}'] = [
            results_re_correct[i],
            results_re_incorrect[i],
            results_lark_correct[i],
            results_lark_incorrect[i],
            result_miles_correct[i],
            results_miles_incorrect[i]
        ]

    df = pd.DataFrame(data)

    print(df.to_string(index=False))