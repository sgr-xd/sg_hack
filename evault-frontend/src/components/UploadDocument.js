// src/components/UploadDocument.js
import React, { useState } from "react";
import axios from "axios";
import './UploadDocument.css';

const UploadDocument = () => {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState("");

  const handleFileChange = (e) => setFile(e.target.files[0]);
  const handleTitleChange = (e) => setTitle(e.target.value);

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title);
    const response = await axios.post("http://127.0.0.1:5000/upload", formData);
    alert(`Document uploaded! TX Hash: ${response.data.tx_hash}`);
  };

  return (
    <div className="upload-container">
      <h2>Upload Document</h2>
      <input
        type="text"
        value={title}
        onChange={handleTitleChange}
        placeholder="Document Title"
      />
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload Document</button>
    </div>
  );
};

export default UploadDocument;
