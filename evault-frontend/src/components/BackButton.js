import React from 'react';
import { useNavigate } from 'react-router-dom';

const BackButton = () => {
    const navigate = useNavigate();

    return (
        <button onClick={() => navigate(-1)} style={{ margin: '10px', padding: '10px' }}>
            Back
        </button>
    );
};

export default BackButton;
