import './App.css';
import Workspace from "./workplace";
import Canvas from "./canvas/page_canvas";
import {Route, BrowserRouter as Router, Routes} from "react-router-dom";

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Workspace><Canvas /></Workspace>} />
            </Routes>
        </Router>
    );
}

export default App;
