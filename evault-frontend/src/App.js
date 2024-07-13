// src/App.js
import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Home from "./components/Home";
import Register from "./components/Register";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";
import UploadDocument from "./components/UploadDocument";
import RetrieveDocument from "./components/RetrieveDocument";
import AllDocuments from "./components/AllDocuments";
import AdminPanel from "./components/AdminPanel";
import "./App.css";

const App = () => {
  return (
    <Router>
      <div className="App">
        <h1>eVault System</h1>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/upload" element={<UploadDocument />} />
          <Route path="/retrieve" element={<RetrieveDocument />} />
          <Route path="/all-documents" element={<AllDocuments />} />
          <Route path="/admin" element={<AdminPanel />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
