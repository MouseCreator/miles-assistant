import './shared.css'

import './workspace.css';



const Workspace = ({ children }) => {
    return (
        <div className="workspace">
            <header className="workspace-header">
                <h1 className="workspace-title">Miles Demo</h1>
                <div className={"workspace-nav"} />
            </header>
            <main className="workspace-content">
                {children}
            </main>
        </div>
    );
};

export default Workspace;