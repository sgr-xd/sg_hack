import React, { useEffect, useState } from "react";
import axios from "axios";
import './AllDocuments.css';

const AdminDocuments = () => {
  const [records, setRecords] = useState([]);

  const fetchRecords = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:5000/get_all_records");
      console.log("Admin records response:", response.data);
      setRecords(response.data);
    } catch (error) {
      console.error('Failed to fetch records:', error);
      alert('Failed to fetch records: ' + (error.response?.data?.error || error.message));
    }
  };

  const downloadDocument = async (recordId) => {
    try {
      const response = await axios.get(`http://localhost:5000/download/${recordId}`, { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const a = document.createElement("a");
      a.href = url;
      a.setAttribute("download", `document_${recordId}.pdf`);
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (error) {
      console.error("Error downloading the document:", error);
    }
  };

  const deleteDocument = async (recordId) => {
    try {
      await axios.post(`http://localhost:5000/delete/${recordId}`);
      fetchRecords();
    } catch (error) {
      console.error("Error deleting document:", error);
    }
  };

  const GCSuploadDocument = async (recordId) => {
    try {
      const response = await axios.post(`http://localhost:5000/upload_to_gcs/${recordId}`);
      if (response.status === 201) {
        alert(response.data.message);
      } else {
        console.error("Unexpected response status:", response.status);
      }
    } catch (error) {
      console.error("Error uploading document:", error);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  return (
    <div className="all-documents">
      <h2>All Documents (Admin)</h2>
      {records.length === 0 ? (
        <p>No documents found.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Owner</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {records.map((record) => (
              <tr key={record.id}>
                <td><strong>{record.id}</strong></td>
                <td><strong>{record.title}</strong></td>
                <td>{record.owner}</td>
                <td className="button-container">
                  <button onClick={() => GCSuploadDocument(record.id)} className="small-button">Upload to Legal DB</button>
                  <button onClick={() => downloadDocument(record.id)} className="small-button">Download</button>
                  <button onClick={() => deleteDocument(record.id)} className="small-button delete-button">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default AdminDocuments;
