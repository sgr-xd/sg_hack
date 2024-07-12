// src/components/RetrieveDocument.js
import React, { useState } from 'react';
import axios from 'axios';

const RetrieveDocument = () => {
    const [id, setId] = useState('');
    const [document, setDocument] = useState(null);

    const handleRetrieve = async () => {
        const response = await axios.get(`http://localhost:5000/get_record/${id}`);
        setDocument(response.data);
    };

    return (
        <div>
            <h2>Retrieve Document</h2>
            <input type="text" value={id} onChange={(e) => setId(e.target.value)} placeholder="Document ID" />
            <button onClick={handleRetrieve}>Retrieve Document</button>
            {document && (
                <div>
                    <h3>Document Details:</h3>
                    <p>ID: {document.id}</p>
                    <p>Hash: {document.hash}</p>
                    <p>Title: {document.title}</p>
                    <p>Owner: {document.owner}</p>
                </div>
            )}
        </div>
    );
};

export default RetrieveDocument;
