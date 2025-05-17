from typing import List

from flask import Flask, request, jsonify
from flask_cors import CORS

from src.miles.core.recognizer.recognizer_error import RecognizerError
from src.miles.shared.matching_core_factory import create_matching_core
from src.miles.shared.register import MilesRegister
from src.server.canvas_context import Shape, RequestContext
from src.server.canvas_grammar import canvas_grammar
from src.server.shape_error import ShapeError
from src.server.voice_to_text import recognize_and_format

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])


plugin = MilesRegister().create_plugin_register('app')
canvas_grammar(plugin)
matching_core = create_matching_core()


def _process_shapes(id_count: int, shape_objects: List[Shape], command: str):
    try:
        context = RequestContext(shape_objects, id_count)
        matching_core.recognize_and_execute(command, 'canvas', context)

        response_data = {
            "id_count": context.identity(),
            "shapes": [shape.to_dict() for shape in context.shapes()]
        }

        return jsonify(response_data), 200

    except RecognizerError as e:
        message = str(e)
        return jsonify({'error': message}), 400
    except ShapeError as e:
        message = str(e)
        return jsonify({'error': message}), 400
    except Exception:
        message = 'Server Error!'
        return jsonify({'error': message}), 500


@app.route('/canvas/audio', methods=['POST'])
def process_shapes_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio = request.files['audio']
    data = request.get_json()
    id_count = int(data['id_count'])
    shape_objects = [
        Shape(
            identity=shape['identity'],
            category=shape['category'],
            x=shape['x'],
            y=shape['y'],
            color=shape['color'],
            angle=shape['angle']
        )
        for shape in data['shapes']
    ]
    command = recognize_and_format(audio)
    return _process_shapes(id_count, shape_objects, command)

@app.route('/canvas/text', methods=['POST'])
def process_shapes_text():
    data = request.get_json()
    print(data)
    if 'id_count' not in data or 'shapes' not in data or 'command' not in data:
        return jsonify({"error": "Invalid request format"}), 400

    shape_objects = [
        Shape(
            identity=shape['identity'],
            category=shape['category'],
            x=shape['x'],
            y=shape['y'],
            color=shape['color'],
            angle=shape['angle']
        )
        for shape in data['shapes']
    ]

    command = data['command']
    print(command)
    return _process_shapes(int(data['id_count']), shape_objects, command)


if __name__ == '__main__':
    app.run(port=5000, debug=True)