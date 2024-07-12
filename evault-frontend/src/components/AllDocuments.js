// src/components/AllDocuments.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';

const AllDocuments = () => {
    const [records, setRecords] = useState([]);

    const fetchRecords = async () => {
        const response = await axios.get('http://localhost:5000/get_all_records');
        setRecords(response.data);
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
                            <strong>{record.title}</strong> (Hash: {record.hash}) - Owner: {record.owner}
                        </li>
                    ))
                )}
            </ul>
        </div>
    );
};

export default AllDocuments;
