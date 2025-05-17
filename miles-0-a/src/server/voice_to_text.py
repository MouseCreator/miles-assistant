import string
import tempfile

import whisper

from src.miles.utils.singleton import Singleton


class VoiceModel(metaclass=Singleton):
    def __init__(self):
        self._model = whisper.load_model("base")

    def get_model(self):
        return self._model


def recognize_and_format(sound_data) -> str:

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
        tmp.write(sound_data)
        tmp.flush()
        model = whisper.load_model("base")
        result = model.transcribe(tmp.name, without_timestamps=True, initial_prompt=None)
        text = result["text"]
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text.strip()