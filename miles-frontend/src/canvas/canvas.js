import React, {useRef, useEffect, useImperativeHandle, forwardRef, useCallback} from 'react';
import './canvas.css'

const CANVAS_WIDTH = 1000;
const CANVAS_HEIGHT = 1000;

const colors = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'violet', 'pink', 'brown'];
const canvas = ['arrow', 'circle', 'square', 'triangle', 'hexagon', 'oval', 'line'];

class Shape {
    constructor(identity, type, x, y, color, angle) {
        this.identity = identity
        this.category = type;
        this.x = x;
        this.y = y;
        this.color = color;
        this.angle = angle
    }

    draw(ctx) {
        ctx.save();
        ctx.fillStyle = this.color;
        ctx.strokeStyle = this.color;
        ctx.lineWidth = 3;
        ctx.rotate((this.angle * Math.PI) / 180);
        const drawX = 0;
        const drawY = 0;

        switch (this.category) {
            case 'circle':
                ctx.beginPath();
                ctx.arc(drawX, drawY, 30, 0, Math.PI * 2);
                ctx.fill();
                break;
            case 'square':
                ctx.fillRect(drawX - 30, drawY - 30, 60, 60);
                break;
            case 'triangle':
                ctx.beginPath();
                ctx.moveTo(drawX, drawY - 35);
                ctx.lineTo(drawX - 30, drawY + 25);
                ctx.lineTo(drawX + 30, drawY + 25);
                ctx.closePath();
                ctx.fill();
                break;
            case 'hexagon':
                const r = 30;
                ctx.beginPath();
                for (let i = 0; i < 6; i++) {
                    const angle = Math.PI / 3 * i;
                    const px = drawX + r * Math.cos(angle);
                    const py = drawY + r * Math.sin(angle);
                    if (i === 0) ctx.moveTo(px, py);
                    else ctx.lineTo(px, py);
                }
                ctx.closePath();
                ctx.fill();
                break;
            case 'oval':
                ctx.beginPath();
                ctx.ellipse(drawX, drawY, 40, 25, 0, 0, 2 * Math.PI);
                ctx.fill();
                break;
            case 'line':
                ctx.beginPath();
                ctx.moveTo(drawX - 30, drawY - 30);
                ctx.lineTo(drawX + 30, drawY + 30);
                ctx.stroke();
                break;
            case 'arrow':
                ctx.beginPath();
                ctx.moveTo(drawX - 30, drawY);
                ctx.lineTo(drawX + 10, drawY);
                ctx.lineTo(drawX + 10, drawY - 10);
                ctx.lineTo(drawX + 30, drawY + 10);
                ctx.lineTo(drawX + 10, drawY + 30);
                ctx.lineTo(drawX + 10, drawY + 20);
                ctx.lineTo(drawX - 30, drawY + 20);
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
            const angle =  getRandomInt(0, 360)
            shapesRef.current.push(new Shape(i+1, type, x, y, color, angle));
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