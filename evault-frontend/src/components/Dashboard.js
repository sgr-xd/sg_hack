import React, { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import './Dashboard.css';
import axios from 'axios';

const Dashboard = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [userType, setUserType] = useState('User'); // Default to 'user'

    useEffect(() => {
        // Check if userType is passed from location state
        const { state } = location;
        if (state && state.userType) {
            setUserType(state.userType);
        } else {
            // Optionally, check session or redirect if needed
            alert('User type not found. Please log in again.');
            navigate('/login');
        }
    }, [location, navigate]);

    const handleLogout = async () => {
        try {
            const response = await axios.post('http://localhost:5000/logout', {}, { withCredentials: true });
            if (response.status === 200) {
                navigate('/login');
            }
        } catch (error) {
            alert('Logout failed: ' + (error.response?.data?.error || error.message));
        }
    };

    return (
        <div className="dashboard">
            <h2>Dashboard</h2>
            <button onClick={handleLogout}>Logout</button>
            <nav className="navbar">
                <Link to="/upload">Upload Document</Link>
                <Link to="/retrieve">Retrieve Document</Link>
                <Link to="/all-documents">All Documents</Link>
                {userType === 'Admin' && <Link to="/admin">Admin Panel</Link>}
            </nav>
        </div>
    );
};

export default Dashboard;
