from flask import Flask, request, jsonify
from flask_cors import CORS

from src.miles.core.recognizer.recognizer_error import RecognizerError
from src.miles.shared.matching_core_factory import create_matching_core
from src.miles.shared.register import MilesRegister
from src.server.canvas_context import Shape, RequestContext
from src.server.canvas_grammar import canvas_grammar
from src.server.shape_error import ShapeError

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])


plugin = MilesRegister().create_plugin_register('app')
canvas_grammar(plugin)
matching_core = create_matching_core()

@app.route('/canvas', methods=['POST'])
def process_shapes():
    try:
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
        id_count = data['id_count']
        context = RequestContext(shape_objects, id_count)
        matching_core.recognize_and_execute(command, 'canvas', context)

        response_data = {
            "id_count": context.identity(),
            "shapes": [shape.to_dict() for shape in context.shapes()]
        }

        return jsonify(response_data), 200

    except RecognizerError as e:
        message = str(e)
        return jsonify({"error": message}), 400
    except ShapeError as e:
        message = str(e)
        return jsonify({"error": message}), 400
    except Exception:
        message = 'Server Error!'
        return jsonify({"error": message}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)