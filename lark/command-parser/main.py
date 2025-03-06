from lark import Lark

grammar = r"""
    start: expr

    expr: WORD          -> word
        | MATCHING      -> matching
        | list
        | choice
        | optional

    choice: "(" expr ("," expr)* ")"  -> choice
    list: "[" expr ("," expr)* "]"    -> list
    optional: "{" expr "}"            -> optional

    WORD: /[A-Z]+/
    MATCHING: /[a-z]+/

    %import common.WS
    %ignore WS
"""

parser = Lark(grammar, start="start", parser="lalr")

# Example test cases
test_cases = [
    "HELLO",
    "world",
    "(HELLO, world, TEST)",
    "[HELLO, test]",
    "{example}"
]
if __name__ == '__main__':
    for test in test_cases:
        tree = parser.parse(test)
        print(tree.pretty())
