import React, { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadDataset } from '../services/api'
import { Upload, FileSpreadsheet, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react'

export default function UploadPage() {
  const [dragActive, setDragActive] = useState(false)
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleDrag = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(e.type === 'dragenter' || e.type === 'dragover')
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files?.[0]) {
      setFile(e.dataTransfer.files[0])
      setError('')
      setResult(null)
    }
  }, [])

  const handleFileSelect = (e) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0])
      setError('')
      setResult(null)
    }
  }

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    setError('')
    try {
      const res = await uploadDataset(file)
      setResult(res)
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Upload Dataset</h1>
        <p className="text-gray-400">Upload CSV, JSON, or Parquet files to your data lake</p>
      </div>

      <div className="max-w-2xl">
        {/* Drop zone */}
        <div
          className={`glass-card p-12 text-center border-2 border-dashed transition-all duration-200 cursor-pointer ${
            dragActive
              ? 'border-brand-500 bg-brand-500/5'
              : 'border-gray-700/50 hover:border-gray-600'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => document.getElementById('file-input').click()}
        >
          <input
            id="file-input"
            type="file"
            accept=".csv,.json,.parquet"
            onChange={handleFileSelect}
            className="hidden"
          />
          <Upload className={`w-12 h-12 mx-auto mb-4 ${dragActive ? 'text-brand-400' : 'text-gray-600'}`} />
          <p className="text-lg font-medium mb-2">
            {file ? file.name : 'Drop your file here or click to browse'}
          </p>
          <p className="text-sm text-gray-500">Supports CSV, JSON, Parquet · Max 50MB</p>
        </div>

        {/* File info */}
        {file && !result && (
          <div className="glass-card p-6 mt-4">
            <div className="flex items-center gap-4 mb-4">
              <FileSpreadsheet className="w-10 h-10 text-brand-400" />
              <div className="flex-1">
                <p className="font-medium">{file.name}</p>
                <p className="text-sm text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
              </div>
            </div>
            <button
              id="upload-btn"
              onClick={handleUpload}
              disabled={uploading}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              {uploading ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Uploading...</>
              ) : (
                <><Upload className="w-4 h-4" /> Upload to Data Lake</>
              )}
            </button>
          </div>
        )}

        {/* Success */}
        {result && (
          <div className="glass-card p-6 mt-4 border border-green-500/20 bg-green-500/5">
            <div className="flex items-center gap-3 mb-4">
              <CheckCircle2 className="w-6 h-6 text-green-400" />
              <h3 className="font-semibold text-green-400">Upload Successful</h3>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm mb-4">
              <div><span className="text-gray-500">Dataset ID:</span> <span className="font-mono">{result.dataset_id}</span></div>
              <div><span className="text-gray-500">Type:</span> {result.file_type?.toUpperCase()}</div>
              <div><span className="text-gray-500">Rows:</span> {result.row_count?.toLocaleString()}</div>
              <div><span className="text-gray-500">Columns:</span> {result.columns?.length}</div>
            </div>
            <div className="mb-4">
              <p className="text-xs text-gray-500 mb-2">Columns detected:</p>
              <div className="flex flex-wrap gap-2">
                {result.columns?.map((col) => (
                  <span key={col} className="px-2 py-1 bg-gray-800 rounded-lg text-xs font-mono">{col}</span>
                ))}
              </div>
            </div>
            <button
              onClick={() => navigate(`/chat/${result.dataset_id}`)}
              className="btn-primary w-full"
            >
              Start Querying →
            </button>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="glass-card p-4 mt-4 border border-red-500/20 bg-red-500/5 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}
      </div>
    </div>
  )
}
