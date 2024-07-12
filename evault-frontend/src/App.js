// src/App.js
import React from 'react';
import UploadDocument from './components/UploadDocument';
import RetrieveDocument from './components/RetrieveDocument';
import AllDocuments from './components/AllDocuments';
import './App.css'
const App = () => {
    return (
        <div className="App">
            <h1>eVault System</h1>
            <UploadDocument />
            <RetrieveDocument />
            <AllDocuments />
        </div>
    );
};

export default App;
