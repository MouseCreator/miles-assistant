
import './error-box.css'
export function ErrorBox({error, lastInput}) {
    const hasError = error !== ''

    if (hasError) {
        return (<div className={"error-box"}>
            <div>Input: '{lastInput}'</div>
            <div>{error}</div>
        </div>)
    }
    else {
        return <div className={"error-box"}></div>
    }
}