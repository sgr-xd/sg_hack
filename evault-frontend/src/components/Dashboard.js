import React from 'react';
import { Link } from 'react-router-dom';
import './Dashboard.css';

const Dashboard = ({ userType }) => {
    return (
        <div className="dashboard">
            <h2>Dashboard</h2>
            <nav className="navbar">
                <Link to="/upload">Upload Document</Link>
                <Link to="/retrieve">Retrieve Document</Link>
                <Link to="/all-documents">All Documents</Link>
                {userType === 'admin' && <Link to="/admin">Admin Panel</Link>}
            </nav>
        </div>
    );
};

export default Dashboard;
