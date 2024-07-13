// src/components/AllDocuments.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';

const AllDocuments = () => {
    const [records, setRecords] = useState([]);

    const fetchRecords = async () => {
        const response = await axios.get('http://localhost:5000/get_all_records');
        setRecords(response.data);
    };

    const downloadDocument = async (recordId) => {
        try {
            const response = await axios.get(`http://localhost:5000/download/${recordId}`, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const a = document.createElement('a');
            a.href = url;
            a.setAttribute('download', `document_${recordId}.pdf`);
            document.body.appendChild(a);
            a.click();
            a.remove();
        } catch (error) {
            console.error('Error downloading the document:', error);
        }
    };

    useEffect(() => {
        fetchRecords();
    }, []);

    return (
        <div>
            <h2>All Documents</h2>
            <ul>
                {records.length === 0 ? (
                    <li>No documents found.</li>
                ) : (
                    records.map(record => (
                        <li key={record.id}>
                            <strong>{record.id}</strong>: <strong>{record.title}</strong> - Owner: {record.owner}
                            <button onClick={() => downloadDocument(record.id)} style={{ marginLeft: '10px' }}>
                                Download
                            </button>
                        </li>
                    ))
                )}
            </ul>
        </div>
    );
};

export default AllDocuments;
