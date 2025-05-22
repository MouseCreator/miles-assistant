
import './error-box.css'
export function ErrorBox({message, color}) {
    const hasError = message !== ''

    if (hasError) {
        return (<div className={"error-box"}>
            <div style={{color: color}}>{message}</div>
        </div>)
    }
    else {
        return <div className={"error-box"}></div>
    }
}