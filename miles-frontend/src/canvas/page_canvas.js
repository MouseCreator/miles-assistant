import {useRef, useState} from "react";
import CanvasShapes from "./canvas";
import InputRow from "../inputs/inputRow";
import {Shape} from "./shape";
import {ErrorBox} from "./error_box";

export default function Canvas() {
    const canvasRef = useRef();

    const [shapes, setShapes] = useState([]);
    const [idCount, setIdCount] = useState(0);
    const [error, setError] = useState('')
    const [lastInput, setLastInput] = useState('')

    function requestServerCommandProcessor(address, init_params) {
        fetch(address, init_params)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        console.error('Server Error:', err.error);
                        setError(err.error)
                        return null;
                    });
                }
                return response.json();
            })
            .then(data => {
                setError('')
                if (data == null) {
                    return;
                }
                setIdCount(data.id_count);
                const mappedShapes = data.shapes.map(item =>
                    new Shape(item.identity, item.category, item.x, item.y, item.color, item.angle)
                );
                setShapes(mappedShapes);
            })
            .catch(error => {
                console.error('Error:', error.message);
                setError('Error!')
            });
    }
    function onSubmit(text) {
        setError('');
        setLastInput(text);
        requestServerCommandProcessor('http://localhost:5000/canvas/text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id_count: idCount,
                command: text,
                shapes: shapes
            })
        })
    }
    function onRecorded(audio) {
        const formData = new FormData();
        formData.append('audio', audio, 'recording.webm');
        formData.append('id_count', idCount);
        formData.append('shapes', JSON.stringify(shapes))
        requestServerCommandProcessor('http://localhost:5000/canvas/audio', {
            method: 'POST',
            body: formData
        });
    }

    return (
        <div>
            <InputRow onSubmit={onSubmit} onRecorded={onRecorded} />
            <ErrorBox error={error} lastInput={lastInput} />
            <CanvasShapes ref={canvasRef} shapes={shapes} />
        </div>
    )
}