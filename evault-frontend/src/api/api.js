import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:5000/api', // Adjust based on your Flask backend
});

export const uploadDocument = (formData) => api.post('/upload', formData);
export const getMyDocuments = () => api.get('/my-documents');
export const getSharedDocuments = () => api.get('/shared-documents');

export default api;
