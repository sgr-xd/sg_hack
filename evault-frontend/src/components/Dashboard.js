import React, { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import "./Dashboard.css";
import axios from "axios";

const Dashboard = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [userType, setUserType] = useState("User"); // Default to 'user'

  useEffect(() => {
    const { state } = location;
    if (state && state.userType) {
      setUserType(state.userType);
    } else {
      alert("User type not found. Please log in again.");
      navigate("/login");
    }
  }, [location, navigate]);

  const handleLogout = async () => {
    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/logout",
        {},
        { withCredentials: true }
      );
      if (response.status === 200) {
        setUserType("User"); // Reset userType to default
        navigate("/login");
      }
    } catch (error) {
      alert("Logout failed: " + (error.response?.data?.error || error.message));
    }
  };
  const handleGenerateLog = async () => {
    try {
      const response = await axios.get("http://localhost:5000/generate_log", {
        withCredentials: true,
        responseType: "blob", // Important for downloading files
      });

      // Create a URL for the file and trigger download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "Log.txt"); // Set default file name
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      console.log("Fetched records and initiated download.");
    } catch (error) {
      alert(
        "Failed to fetch records: " +
          (error.response?.data?.error || error.message)
      );
    }
  };
  const handleBackup = async () => {
    try {
      const response = await axios.post("http://localhost:5000/backup", {
        withCredentials: true,
        responseType: "json", // Use 'json' since you expect a JSON response
      });
      console.log("Fetched records and initiated Backup.");
      console.log(response.data.backup_entries); // Log backup entries if needed
      alert("Backup completed successfully!");
    } catch (error) {
      alert(
        "Failed to fetch records: " +
        (error.response?.data?.error || error.message)
      );
    }
  };
  
  return (
    <div className="dashboard">
      <button className="logout-button" onClick={handleLogout}>
        Logout
      </button>
      <h2>{userType} Dashboard</h2>
      <div className="cards">
        <Link to="/upload" className="card">
          Upload Document
        </Link>
        <Link to="/retrieve" className="card">
          Retrieve Document
        </Link>
        <Link className="card" to="/all-documents" state={{ userType: userType }}>All Documents</Link>
        {userType === "Admin" && (
          <Link to="#" className="card generate-log" onClick={handleGenerateLog}>
          Generate Log
        </Link>
        )}
        {userType === "Admin" && (
          <Link to="#" className="card generate-log" onClick={handleBackup}>
          Backup
        </Link>
        )}
        {userType === "Admin" && (
          <Link to="/file-list" className="card generate-log" state={{ userType: userType }}>
          Import From Legal Database
        </Link>
        )}
        
        {userType === "Admin" && (
          <Link to="/admin" className="card">
            List Users
          </Link>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
