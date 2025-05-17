import whisper
import os

def transcribe_audio(model, file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Transcribing {file_path}...")
    result = model.transcribe(file_path)

    print("\n--- Transcription ---\n")
    print(result['text'])
    return result["text"]

if __name__ == "__main__":
    print("Loading model...")
    model = whisper.load_model("base")

    directory = '../../resources/'

    mp3_files = []

    for filename in os.listdir(directory):
        if filename.endswith('.mp3'):
            full_name= os.path.join(directory, filename)
            mp3_files.append(full_name)

    for filename in mp3_files:
        transcribe_audio(model, filename)

        base_name = os.path.splitext(filename)[0]
        txt_file = os.path.join(base_name + '.txt')
        with open(txt_file, 'r') as file:
            content = file.read()
            print('Expected:')
            print(f' {content}')