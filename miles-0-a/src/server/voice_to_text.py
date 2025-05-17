import string

import whisper

from src.miles.utils.singleton import Singleton


class VoiceModel(metaclass=Singleton):
    def __init__(self):
        self._model = whisper.load_model("base")

    def get_model(self):
        return self._model


def recognize_and_format(filepath) -> str:
    model = whisper.load_model("base")
    result = model.transcribe(filepath, without_timestamps=True, initial_prompt=None)
    text = result["text"]
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text.strip()