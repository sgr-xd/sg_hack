import React, { useEffect, useState } from "react";
import axios from "axios";
import { useLocation, useNavigate } from "react-router-dom";
import './AllDocuments.css';
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
      fetchRecords();
    } catch (error) {
      console.error("Error deleting document:", error);
    }
  };

  const GCSuploadDocument = async (recordId) => {
    try {
      const response = await axios.post(`http://localhost:5000/upload_to_gcs/${recordId}`);
      
      // Check if the response status is 201 (Created) which means the file upload was successful
      if (response.status === 201) {
        console.log(response.data.message);
        alert(response.data.message)
      } else {
        console.error("Unexpected response status:", response.status);
      }
    } catch (error) {
      if (error.response) {
        // The request was made, but the server responded with a status code that falls out of the range of 2xx
        console.error("Error response data:", error.response.data);
        console.error("Error response status:", error.response.status);
        console.error("Error response headers:", error.response.headers);
      } else if (error.request) {
        // The request was made but no response was received
        console.error("Error request data:", error.request);
      } else {
        // Something happened in setting up the request that triggered an Error
        console.error("Error message:", error.message);
      }
      console.error("Error config:", error.config);
    }
  };
  
  useEffect(() => {
    if (userType) {
      fetchRecords();
    }
  }, [userType]);

  return (
    <div className="all-documents">
    <h2>All Documents</h2>
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

export default AllDocuments;
