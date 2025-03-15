from abc import ABC, abstractmethod

from src.miles.core.recognizer.recognize_context import RecognizeContext


class GenericContextAnalyzer(ABC):

    @abstractmethod
    def invoke(self, context: RecognizeContext):
        pass

    def process(self, context: RecognizeContext):
        if context.is_empty():
            context.fail()
        else:
            self.invoke(context)


class WordContextAnalyzer(GenericContextAnalyzer):
    """
    Word Context Analyzer implements matching for a single word
    It checks if the current token equals to the expected one. The token is consumed if it is expected, else the recognition fails
    """
    def __init__(self, word: str):
        self.word = word.lower()

    def invoke(self, context: RecognizeContext):
        current_token = context.current()
        if current_token == self.word:
            context.consume()
        else:
            context.fail()

class TextContextAnalyzer(GenericContextAnalyzer):
    """
    Text Context Analyzer implements matching for unbounded text
    """
    def __init__(self):
        pass

    def invoke(self, context: RecognizeContext):
        while context.has_any():
            context.consume(interrupted=True)

class AutomaticContextAnalyzer(GenericContextAnalyzer):
    """
   Automatic Context Analyzer implements matching for automatic transitions, e.g. unconditional pointer moving with no token consumption
   """
    def __init__(self):
        pass

    def process(self, context: RecognizeContext):
        pass

    def invoke(self, context: RecognizeContext):
        pass
