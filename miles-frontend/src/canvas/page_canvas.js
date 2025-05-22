import {useRef, useState} from "react";
import CanvasShapes from "./canvas";
import InputRow from "../inputs/inputRow";
import {Shape} from "./shape";
import {ErrorBox} from "./error_box";

export default function Canvas() {
    const canvasRef = useRef();

    const [shapes, setShapes] = useState([]);
    const [idCount, setIdCount] = useState(0);
    const [message, setMessage] = useState('Welcome!')
    const [color, setColor] = useState('black')

    function requestServerCommandProcessor(address, init_params) {
        fetch(address, init_params)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        console.error('Server Error:', err.error);
                        setMessage(err.error)
                        setColor('red')
                        return null;
                    });
                }
                return response.json();
            })
            .then(data => {

                if (data == null) {
                    return;
                }
                setIdCount(data.id_count);
                const mappedShapes = data.shapes.map(item =>
                    new Shape(item.identity, item.category, item.x, item.y, item.color, item.angle)
                );
                setShapes(mappedShapes);
                setMessage('Done!')
                setColor('green')
            })
            .catch(error => {
                console.error('Error:', error.message);
                setMessage('Error!')
            });
    }
    function onSubmit(text) {
        setMessage('Processing...');
        setColor('black')
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
        setMessage('Processing...');
        setColor('black')
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
            <ErrorBox message={message} color={color} />
            <CanvasShapes ref={canvasRef} shapes={shapes} />
        </div>
    )
}