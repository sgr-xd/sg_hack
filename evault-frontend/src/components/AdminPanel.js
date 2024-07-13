import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
const AdminPanel = () => {
    const [users, setUsers] = useState([]);
    const navigate = useNavigate();
    useEffect(() => {
        const fetchUsers = async () => {
            const response = await fetch('http://localhost:5000//admin/users');
            const data = await response.json();
            setUsers(data);
        };

        fetchUsers();
    }, []);
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
        <div className="admin-panel">
            <h2>Admin Panel</h2>
            <button onClick={handleLogout}>Logout</button>
            <ul>
                {users.map((user) => (
                    <li key={user._id}>{user.username} - {user.user_type}</li>
                ))}
            </ul>
        </div>
    );
};

export default AdminPanel;
