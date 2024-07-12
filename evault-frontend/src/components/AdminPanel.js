import React, { useEffect, useState } from 'react';

const AdminPanel = () => {
    const [users, setUsers] = useState([]);

    useEffect(() => {
        const fetchUsers = async () => {
            const response = await fetch('http://localhost:5000/users');
            const data = await response.json();
            setUsers(data);
        };

        fetchUsers();
    }, []);

    return (
        <div className="admin-panel">
            <h2>Admin Panel</h2>
            <ul>
                {users.map((user) => (
                    <li key={user._id}>{user.username} - {user.user_type}</li>
                ))}
            </ul>
        </div>
    );
};

export default AdminPanel;
