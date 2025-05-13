import React, {useRef, useEffect, useImperativeHandle, forwardRef, useCallback} from 'react';
import './canvas.css'

const CANVAS_WIDTH = 1000;
const CANVAS_HEIGHT = 1000;

const colors = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'violet', 'pink', 'black', 'brown'];
const canvas = ['arrow', 'circle', 'square', 'triangle', 'hexagon', 'oval', 'line'];

class Shape {
    constructor(type, x, y, color) {
        this.type = type;
        this.x = x;
        this.y = y;
        this.color = color;
    }

    draw(ctx) {
        ctx.save();
        ctx.fillStyle = this.color;
        ctx.strokeStyle = this.color;
        ctx.lineWidth = 3;

        const x = this.x;
        const y = this.y;

        switch (this.type) {
            case 'circle':
                ctx.beginPath();
                ctx.arc(x, y, 30, 0, Math.PI * 2);
                ctx.fill();
                break;
            case 'square':
                ctx.fillRect(x - 30, y - 30, 60, 60);
                break;
            case 'triangle':
                ctx.beginPath();
                ctx.moveTo(x, y - 35);
                ctx.lineTo(x - 30, y + 25);
                ctx.lineTo(x + 30, y + 25);
                ctx.closePath();
                ctx.fill();
                break;
            case 'hexagon':
                const r = 30;
                ctx.beginPath();
                for (let i = 0; i < 6; i++) {
                    const angle = Math.PI / 3 * i;
                    const px = x + r * Math.cos(angle);
                    const py = y + r * Math.sin(angle);
                    if (i === 0) ctx.moveTo(px, py);
                    else ctx.lineTo(px, py);
                }
                ctx.closePath();
                ctx.fill();
                break;
            case 'oval':
                ctx.beginPath();
                ctx.ellipse(x, y, 40, 25, 0, 0, 2 * Math.PI);
                ctx.fill();
                break;
            case 'line':
                ctx.beginPath();
                ctx.moveTo(x - 30, y - 30);
                ctx.lineTo(x + 30, y + 30);
                ctx.stroke();
                break;
            case 'arrow':
                ctx.beginPath();
                ctx.moveTo(x - 30, y);
                ctx.lineTo(x + 10, y);
                ctx.lineTo(x + 10, y - 10);
                ctx.lineTo(x + 30, y + 10);
                ctx.lineTo(x + 10, y + 30);
                ctx.lineTo(x + 10, y + 20);
                ctx.lineTo(x - 30, y + 20);
                ctx.closePath();
                ctx.fill();
                break;
        }

        ctx.restore();
    }
}
function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

// React component
const CanvasShapes = forwardRef((props, ref) => {
    const canvasRef = useRef(null);
    const shapesRef = useRef([]);

    const drawAll = () => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        shapesRef.current.forEach(shape => shape.draw(ctx));
    };

    const generateShapes = useCallback(() => {
        const total = getRandomInt(4, 12);
        shapesRef.current = [];

        for (let i = 0; i < total; i++) {
            const type = canvas[getRandomInt(0, canvas.length - 1)];
            const color = colors[getRandomInt(0, colors.length - 1)];
            const x = getRandomInt(0, CANVAS_WIDTH);
            const y = getRandomInt(0, CANVAS_HEIGHT);
            shapesRef.current.push(new Shape(type, x, y, color));
        }
        drawAll();
    }, []);

    useEffect(() => {
        generateShapes();
        const handleResize = () => {
            if (canvasRef.current) {
                canvasRef.current.style.width = window.innerWidth + 'px';
                canvasRef.current.style.height = window.innerHeight + 'px';
            }
        };
        handleResize();
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, [generateShapes]);

    // Expose API to parent via ref
    useImperativeHandle(ref, () => ({
        getShapes: () => shapesRef.current,
        redraw: drawAll,
        regenerate: generateShapes,
    }));

    return (
        <div className={'canvas-wrapper '}>
            <canvas className='main-canvas'
                    ref={canvasRef}
                    width={CANVAS_WIDTH}
                    height={CANVAS_HEIGHT}
            />
        </div>
    );
});

export default CanvasShapes;