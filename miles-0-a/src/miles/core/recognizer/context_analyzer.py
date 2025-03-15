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

    def __init__(self, word: str):
        self.word = word.lower()

    def invoke(self, context: RecognizeContext):
        current_token = context.current()
        if current_token == self.word:
            context.consume()
        else:
            context.fail()

class TextContextAnalyzer(GenericContextAnalyzer):

    def __init__(self):
        pass

    def invoke(self, context: RecognizeContext):
        while context.has_any():
            context.consume(interrupted=True)

