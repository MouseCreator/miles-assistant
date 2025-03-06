from src.miles.core.matcher.command_pool import CommandPool


class _Matching:
    def __init__(self, pool : CommandPool, text: str):
        self._pool = pool
        self._text = text

    def match(self):
        pass
        # words = text_to_words(self._text)
        # matcher = pool_to_matcher(pool)

        # find_match(matcher, words)



class TextCommandMatcher:

    def __init__(self, pool : CommandPool):
        self._pool = pool

    def match(self, input_text: str):
        pass