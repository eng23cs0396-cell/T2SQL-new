import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000,
});

// Health & System
export const getHealth = () => api.get('/health');
export const getAvailableModels = () => api.get('/models');

// Database API
export const listDatabases = () => api.get('/database/list');
export const uploadDatabase = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/database/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};
export const getDatabaseSchema = (databaseId) => api.get(`/database/${encodeURIComponent(databaseId)}/schema`);
export const getDatabaseTables = (databaseId) => api.get(`/database/${encodeURIComponent(databaseId)}/tables`);
export const getTablePreview = (databaseId, tableName, limit = 10) =>
  api.get(`/database/${encodeURIComponent(databaseId)}/preview/${encodeURIComponent(tableName)}?limit=${limit}`);

// Text-to-SQL Generation & Execution
export const generateSQL = (payload) => api.post('/generate', payload);
export const executeSQL = (payload) => api.post('/execute', payload);
export const compareModels = (payload) => api.post('/compare', payload);

// Fine-Tuning Lab
export const listAdapters = () => api.get('/finetuning/adapters');
export const getFinetuningPreflight = (config) => api.post('/finetuning/preflight', config);
export const startFinetuning = (config) => api.post('/finetuning/start', config);
export const getFinetuningStatus = (jobId) => api.get(`/finetuning/status/${jobId}`);

// Evaluation Dashboard
export const runEvaluation = (payload) => api.post('/evaluation/run', payload);
export const getEvaluationStatus = (jobId) => api.get(`/evaluation/status/${jobId}`);
export const getLatestEvaluationResults = () => api.get('/evaluation/results');
export const getExportUrl = (format = 'json', modelType = null) => {
  let url = `${API_BASE}/evaluation/export?format=${format}`;
  if (modelType) url += `&model_type=${modelType}`;
  return url;
};

export default api;

