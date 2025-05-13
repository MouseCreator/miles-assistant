import {useRef} from "react";
import CanvasShapes from "./canvas";
import InputRow from "../inputs/inputRow";


export default function Canvas() {
    const canvasRef = useRef();

    function onSubmit(text) {

    }
    function onRecorded(audio) {

    }

    return (
        <div>
            <InputRow onSubmit={onSubmit} onRecorded={onRecorded} />
            <CanvasShapes ref={canvasRef} />
        </div>
    )
}