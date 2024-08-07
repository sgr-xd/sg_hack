import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Login.css';
const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
          const response = await axios.post('http://127.0.0.1:5000/login', {
            username,
            password,
          }, { withCredentials: true });
      
          if (response.status === 200) {
            const userType = response.data.user_type;
            localStorage.setItem('userType', userType);
            navigate('/dashboard', { state: { userType } });
          }
        } catch (error) {
          console.error('Login error:', error);
          alert('Login failed: ' + (error.response?.data?.error || error.message));
        }
      };
    

    return (
        <form className="login" onSubmit={handleLogin}>
            <h2>Login</h2>
            <input type="text" placeholder="Username" onChange={(e) => setUsername(e.target.value)} />
            <input type="password" placeholder="Password" onChange={(e) => setPassword(e.target.value)} />
            <button type="submit">Login</button>
        </form>
    );
};

export default Login;
