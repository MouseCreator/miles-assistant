
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
        ctx.rotate((this.angle * Math.PI) / 180);
        const drawX = this.x;
        const drawY = this.y;

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

        ctx.fillStyle = 'black';
        ctx.font = '28px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(this.identity, this.x, this.y);
    }
}