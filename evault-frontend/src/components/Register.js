import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Register.css';
const Register = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [userType, setUserType] = useState('User');
    const navigate = useNavigate();

    const handleRegister = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://127.0.0.1:5000/register', {
                username,
                password,
                user_type: userType,
            });
            if (response.status === 200 || response.status ===201) {
                navigate('/login');
            } else {
                alert('Registration failed');
            }
        } catch (error) {
            console.error('Error registering user:', error);
            alert('Registration failed');
        }
    };

    return (
        <form className='register' onSubmit={handleRegister}>
            <h2>Register</h2>
            <input 
                type="text" 
                placeholder="Username" 
                value={username} 
                onChange={(e) => setUsername(e.target.value)} 
            />
            <input 
                type="password" 
                placeholder="Password" 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
            />
            <select value={userType} onChange={(e) => setUserType(e.target.value)}>
                <option value="User">User</option>
                <option value="Lawyer">Lawyer</option>
            </select>
            <button type="submit">Register</button>
        </form>
    );
};

export default Register;
