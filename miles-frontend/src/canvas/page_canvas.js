import {useRef, useState} from "react";
import CanvasShapes from "./canvas";
import InputRow from "../inputs/inputRow";
import {Shape} from "./shape";


export default function Canvas() {
    const canvasRef = useRef();

    const [shapes, setShapes] = useState([]);
    const [idCount, setIdCount] = useState(0);
    function onSubmit(text) {
        fetch('http://localhost:5000/canvas', {
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
            .then(response => response.json())
            .then(data => {
                setIdCount(data.id_count)
                const mappedShapes = data.shapes.map(item =>
                    new Shape(item.identity, item.category, item.x, item.y, item.color, item.angle)
                );

                setShapes(mappedShapes);
            })
            .catch(error => console.error('Error:', error));
    }
    function onRecorded(audio) {

    }

    return (
        <div>
            <InputRow onSubmit={onSubmit} onRecorded={onRecorded} />
            <CanvasShapes ref={canvasRef} shapes={shapes} />
        </div>
    )
}