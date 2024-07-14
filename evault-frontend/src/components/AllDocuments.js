import React, { useEffect, useState } from "react";
import axios from "axios";
import { useLocation, useNavigate } from "react-router-dom";

const AllDocuments = () => {
  const [records, setRecords] = useState([]);
  const location = useLocation();
  const navigate = useNavigate();
  const [userType, setUserType] = useState("User");

  useEffect(() => {
    if (location.state && location.state.userType) {
      setUserType(location.state.userType);
    } else {
      const storedUserType = localStorage.getItem('userType');
      if (storedUserType) {
        setUserType(storedUserType);
      } else {
        alert("User type not found. Please log in again.");
        navigate("/login");
      }
    }
  }, [location.state, navigate]);

  const fetchRecords = async () => {
    try {
      if (userType === "Admin") {
        const response = await axios.get("http://127.0.0.1:5000/get_all_records");
        console.log("Admin records response:", response.data);
        setRecords(response.data);
      } else {
        const response = await axios.get("http://127.0.0.1:5000/get_recordIds");
        console.log("NON-Admin records response:", response.data);
        const recordIds = response.data.record_ids;
  
        const recordDetailsPromises = recordIds.map(async (id) => {
          const recordResponse = await axios.get(`http://localhost:5000/get_record/${id}`);
          return recordResponse.data;
        });
  
        const detailedRecords = await Promise.all(recordDetailsPromises);
        setRecords(detailedRecords);
      }
    } catch (error) {
      console.error('Failed to fetch records:', error);
      alert('Failed to fetch records: ' + (error.response?.data?.error || error.message));
    }
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
      await axios.post(`http://localhost:5000/delete/${recordId}`);
      fetchRecords(); // Refresh the list after deletion
    } catch (error) {
      console.error("Error deleting document:", error);
    }
  };

  useEffect(() => {
    if (userType) {
      fetchRecords();
    }
  }, [userType]);

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
