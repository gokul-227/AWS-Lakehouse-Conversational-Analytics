import axios from 'axios';
import { fetchAuthSession } from 'aws-amplify/auth';

const API_BASE = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use(async (config) => {
  try {
    const session = await fetchAuthSession();
    const token = session.tokens.idToken.toString();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  } catch (err) {
    // No session
  }
  return config;
});


// ── Datasets ────────────────────────────────────────────────────

export const uploadDataset = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  const res = await api.post('/datasets/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

export const listDatasets = async () => {
  const res = await api.get('/datasets/')
  return res.data
}

export const getDataset = async (id) => {
  const res = await api.get(`/datasets/${id}`)
  return res.data
}

export const previewDataset = async (id, rows = 10) => {
  const res = await api.get(`/datasets/${id}/preview?rows=${rows}`)
  return res.data
}

export const deleteDataset = async (id) => {
  const res = await api.delete(`/datasets/${id}`)
  return res.data
}

// ── Queries ─────────────────────────────────────────────────────

export const askQuestion = async (question, datasetId) => {
  const res = await api.post('/queries/ask', { question, dataset_id: datasetId })
  return res.data
}

export const getQueryHistory = async (datasetId = null) => {
  const params = datasetId ? `?dataset_id=${datasetId}` : ''
  const res = await api.get(`/queries/history${params}`)
  return res.data
}

export const getQuery = async (id) => {
  const res = await api.get(`/queries/${id}`)
  return res.data
}

// ── Health ──────────────────────────────────────────────────────

export const healthCheck = async () => {
  const res = await api.get('/health')
  return res.data
}

export default api
