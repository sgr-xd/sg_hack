import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./AdminPanel.css";
const AdminPanel = () => {
  const [users, setUsers] = useState([]);
  const navigate = useNavigate();
  useEffect(() => {
    const fetchUsers = async () => {
      const response = await fetch("http://127.0.0.1:5000/admin/users");
      const data = await response.json();
      setUsers(data);
    };

    fetchUsers();
  }, []);
  const handleLogout = async () => {
    try {
      const response = await axios.post(
        "http://localhost:5000/logout",
        {},
        { withCredentials: true }
      );
      if (response.status === 200) {
        navigate("/login");
      }
    } catch (error) {
      alert("Logout failed: " + (error.response?.data?.error || error.message));
    }
  };
  return (
    <div className="admin-panel">
      <h2>Admin Panel</h2>
      <div className="user-list-header">
        <span className="username-header">Username</span>
        <span className="user-type-header">User Type</span>
      </div>
      <ul>
        {users.map((user) => (
          <li key={user._id}>
            <span className="username">{user.username}</span>
            <span className="user-type">{user.user_type}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AdminPanel;
