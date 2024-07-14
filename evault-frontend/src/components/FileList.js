import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './FileList.css';
const FileList = () => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const response = await axios.get('http://localhost:5000/list_files');
        setFiles(response.data.files);
      } catch (err) {
        setError('Error fetching file list');
      } finally {
        setLoading(false);
      }
    };

    fetchFiles();
  }, []);

  const handleImport = async (file) => {
    const title = prompt('Please enter a title for the file:');
  
    if (!title) {
      alert('Title is required!');
      return;
    }
    const formData = new FormData();
    formData.append('file_name', file);
    formData.append('title', title);
    try {
        const response = await axios.post('http://localhost:5000/upload_from_gcs', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
      alert("File Imported successfully!");
      console.log(`File imported successfully: ${response.data}`);
    } catch (error) {
      console.error('Error importing file:', error.response?.data || error.message);
      alert('Error importing file: ' + (error.response?.data?.error || error.message));
    }
  };

  return (
    <div className="file-list">
      <h2>Available Files</h2>
      {loading && <p>Loading...</p>}
      {error && <p>{error}</p>}
      <table>
        <thead>
          <tr>
            <th>File Name</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {files.length === 0 ? (
            <tr>
              <td colSpan="2">No files available.</td>
            </tr>
          ) : (
            files.map((file, index) => (
              <tr key={index}>
                <td>{file}</td>
                <td>
                  <button
                    onClick={() => handleImport(file)}
                    className="small-button"
                  >
                    Import
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default FileList;
