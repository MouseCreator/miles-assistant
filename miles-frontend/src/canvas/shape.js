
export class Shape {
    constructor(identity, category, x, y, color, angle) {
        this.identity = identity
        this.category = category;
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
        ctx.translate(this.x, this.y);
        ctx.rotate((this.angle * Math.PI) / 180);

        switch (this.category) {
            case 'circle':
                ctx.beginPath();
                ctx.arc(0, 0, 30, 0, Math.PI * 2);
                ctx.fill();
                break;
            case 'square':
                ctx.fillRect(-30, -30, 60, 60);
                break;
            case 'triangle':
                ctx.beginPath();
                ctx.moveTo(0, -35);
                ctx.lineTo(-30, 25);
                ctx.lineTo(30, 25);
                ctx.closePath();
                ctx.fill();
                break;
            case 'hexagon':
                const r = 30;
                ctx.beginPath();
                for (let i = 0; i < 6; i++) {
                    const angle = Math.PI / 3 * i;
                    const px = r * Math.cos(angle);
                    const py = r * Math.sin(angle);
                    if (i === 0) ctx.moveTo(px, py);
                    else ctx.lineTo(px, py);
                }
                ctx.closePath();
                ctx.fill();
                break;
            case 'oval':
                ctx.beginPath();
                ctx.ellipse(0, 0, 40, 25, 0, 0, 2 * Math.PI);
                ctx.fill();
                break;
            case 'line':
                ctx.beginPath();
                ctx.moveTo(-30, -30);
                ctx.lineTo(30, 30);
                ctx.stroke();
                break;
            case 'arrow':
                ctx.beginPath();
                ctx.moveTo(-30, 0);
                ctx.lineTo(10, 0);
                ctx.lineTo(10, -10);
                ctx.lineTo(30, 10);
                ctx.lineTo(10, 30);
                ctx.lineTo(10, 20);
                ctx.lineTo(-30, 20);
                ctx.closePath();
                ctx.fill();
                break;
            default:
                break;
        }

        ctx.restore();

        ctx.fillStyle = 'black';
        ctx.font = '28px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(this.identity, this.x, this.y);
    }
}