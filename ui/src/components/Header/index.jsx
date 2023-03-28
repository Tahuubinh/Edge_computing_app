import { routingPaths } from '../routers';
import { NavLink } from 'react-router-dom';
import logo from './logo.png';
import './styles.scss';

export default function Header() {
    return (
        <>
            <div>
                <div className="header">
                    <a className="header-link" href={routingPaths.home}>
                        <img src={logo} alt="homepage" />
                        <div className="logo-text">Edge Computing Optimization</div>
                    </a>
                    <div className="header-btn">
                        <NavLink
                            className="header-btn-link"
                            to={routingPaths.overview}
                        >
                            Overview
                        </NavLink>
                    </div>
                    <div className="header-btn">
                        <NavLink
                            className="header-btn-link"
                            to={routingPaths.detailAlgorithm}
                        >
                            Detail Algorithm
                        </NavLink>
                    </div>
                </div>
            </div>
        </>
    );
}
