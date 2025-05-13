import './App.css';
import Workspace from "./workplace";
import {Home} from "./home/home";
import Canvas from "./canvas/page_canvas";
import {Route, BrowserRouter as Router, Routes} from "react-router-dom";

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Workspace><Home /></Workspace>} />
                <Route path="/canvas" element={<Workspace><Canvas /></Workspace>} />
                <Route path="/calendar" element={<Workspace><Home /></Workspace>} />
                <Route path="/assistant" element={<Workspace><Home /></Workspace>} />
                <Route path="/help" element={<Workspace><Home /></Workspace>} />
            </Routes>
        </Router>
    );
}

export default App;
