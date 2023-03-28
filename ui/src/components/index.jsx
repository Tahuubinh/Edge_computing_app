import Header from './Header';
import { Outlet } from 'react-router-dom';
import './styles.scss'

export default function App() {
    return (
        <>
            <div className="app">
                <Header />
                <div className="app-body">
                    <Outlet />
                </div>
            </div>
        </>
    );
}
