import React, {useRef, useEffect} from 'react';
import './canvas.css'

const CANVAS_WIDTH = 1000;
const CANVAS_HEIGHT = 1000;


export function CanvasShapes({shapes}) {
    const canvasRef = useRef(null);

    const drawAll = () => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        shapes.forEach(shape => shape.draw(ctx));
    };

    useEffect(() => {
        drawAll()
    })


    useEffect(() => {
        const handleResize = () => {
            if (canvasRef.current) {
                canvasRef.current.style.width = window.innerWidth + 'px';
                canvasRef.current.style.height = window.innerHeight + 'px';
            }
        };
        handleResize();
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    return (
        <div className={'canvas-wrapper'}>
            <div className={"canvas-min"}>
                <div>0</div>
            </div>
            <canvas className='main-canvas'
                    ref={canvasRef}
                    width={CANVAS_WIDTH}
                    height={CANVAS_HEIGHT}
            />
            <div className={"canvas-max"}>
                <div>1000</div>
            </div>
        </div>
    );
}

export default CanvasShapes;