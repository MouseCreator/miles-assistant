import './guide.css'
export function Guide() {
    const commands = [
        "ADD { color } shape AT coordinates",
        "SET id COLOR color",
        "SET id SHAPE shape",
        "SET id ANGLE number",
        "SET id X number",
        "SET id Y number",
        "MOVE id TO { COORDINATES } number number",
        "DELETE id",
        "CLEAR { ALL }",
    ]
    return (<div className={"guide-main"}>
        <div className={"guide-header"}>Command Guide</div>
        <div className={"guide-rule"}>
            {commands.map((cmd, idx) => (
                <div key={idx}>{cmd}</div>
            ))}
        </div>
        <div className={"guide-hint"}><strong>Shapes:</strong> arrow, circle, square, triangle, hexagon, oval,<br/> line.</div>
        <div className={"guide-hint"}><strong>Colors:</strong> red, orange, yellow, green, cyan, blue, violet,<br/>pink, brown.</div>
    </div>)
}