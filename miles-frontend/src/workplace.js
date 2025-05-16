import './shared.css'

import { Link } from 'react-router-dom';
import './workspace.css';

const navItems = [
    { name: 'Home', path: '/' },
    { name: 'Canvas', path: '/canvas' },
    { name: 'Help', path: '/help' },
];

const Workspace = ({ children }) => {
    return (
        <div className="workspace">
            <header className="workspace-header">
                <h1 className="workspace-title">Miles Framework Demo</h1>
                <nav className="workspace-nav">
                    {navItems.map((item) => (
                        <Link
                            key={item.name}
                            to={item.path}
                            className={`nav-link ${item.path ? 'active' : ''}`}
                        >
                            {item.name}
                        </Link>
                    ))}
                </nav>
            </header>
            <main className="workspace-content">
                {children}
            </main>
        </div>
    );
};

export default Workspace;