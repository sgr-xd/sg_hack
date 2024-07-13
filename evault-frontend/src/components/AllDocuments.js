// src/components/AllDocuments.js
import React, { useEffect, useState } from "react";
import axios from "axios";

const AllDocuments = () => {
  const [records, setRecords] = useState([]);

  const fetchRecords = async () => {
    const response = await axios.get("http://localhost:5000/get_all_records");
    setRecords(response.data);
  };

  const downloadDocument = async (recordId) => {
    try {
      const response = await axios.get(
        `http://localhost:5000/download/${recordId}`,
        {
          responseType: "blob",
        }
      );
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
      console.log(recordId);
      await axios.delete(`http://localhost:5000/delete/${recordId}`);
      fetchRecords(); // Refresh the list after deletion
    } catch (error) {
      console.error("Error deleting document:", error);
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
          records.map((record) => (
            <li
              key={record.id}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <strong>{record.id}</strong>: <strong>{record.title}</strong> -
                Owner: {record.owner}
              </div>
              <div className="button-container">
                <button
                  onClick={() => downloadDocument(record.id)}
                  className="small-button"
                >
                  Download
                </button>
                <button
                  onClick={() => deleteDocument(record.id)}
                  className="small-button delete-button"
                >
                  Delete
                </button>
              </div>
            </li>
          ))
        )}
      </ul>
    </div>
  );
};

export default AllDocuments;
