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
    translator = str.maketrans({key: ' ' for key in string.punctuation})
    text = text.translate(translator)
    return text.strip()