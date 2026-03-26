import React, { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import { askQuestion, listDatasets, getQueryHistory } from '../services/api'
import ChartRenderer from '../components/ChartRenderer'
import QueryHistory from '../components/QueryHistory'
import DatasetBrowser from '../components/DatasetBrowser'
import { Send, Loader2, Code2, Clock, BarChart3 } from 'lucide-react'

export default function ChatPage() {
  const { datasetId: paramId } = useParams()
  const [datasets, setDatasets] = useState([])
  const [selectedDataset, setSelectedDataset] = useState(paramId || '')
  const [question, setQuestion] = useState('')
  const [conversations, setConversations] = useState([])
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState([])
  const chatEndRef = useRef(null)

  useEffect(() => {
    listDatasets().then((res) => {
      setDatasets(res.datasets || [])
      if (paramId && !selectedDataset) setSelectedDataset(paramId)
    }).catch(() => {})

    getQueryHistory().then((res) => setHistory(res.queries || [])).catch(() => {})
  }, [])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [conversations])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!question.trim() || !selectedDataset || loading) return

    const userMsg = { role: 'user', content: question }
    setConversations((prev) => [...prev, userMsg])
    setQuestion('')
    setLoading(true)

    try {
      const result = await askQuestion(question, selectedDataset)
      const aiMsg = { role: 'assistant', data: result }
      setConversations((prev) => [...prev, aiMsg])
      setHistory((prev) => [result, ...prev])
    } catch (err) {
      const errorMsg = { role: 'assistant', error: err.response?.data?.detail || 'Query failed' }
      setConversations((prev) => [...prev, errorMsg])
    } finally {
      setLoading(false)
    }
  }

  const selectedDs = datasets.find((d) => d.dataset_id === selectedDataset)

  return (
    <div className="flex gap-6 h-[calc(100vh-8rem)]">
      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        <div className="mb-4">
          <h1 className="text-3xl font-bold mb-2">Chat with Your Data</h1>
          <p className="text-gray-400">Ask questions in natural language</p>
        </div>

        {/* Dataset selector */}
        <div className="glass-card p-4 mb-4">
          <label className="text-sm text-gray-400 mb-2 block">Select Dataset</label>
          <select
            id="dataset-select"
            value={selectedDataset}
            onChange={(e) => setSelectedDataset(e.target.value)}
            className="input-field w-full"
          >
            <option value="">Choose a dataset...</option>
            {datasets.map((ds) => (
              <option key={ds.dataset_id} value={ds.dataset_id}>
                {ds.name} ({ds.row_count?.toLocaleString()} rows)
              </option>
            ))}
          </select>
        </div>

        {/* Chat messages */}
        <div className="flex-1 overflow-auto space-y-4 mb-4">
          {conversations.length === 0 && (
            <div className="text-center py-16">
              <BarChart3 className="w-16 h-16 text-gray-700 mx-auto mb-4" />
              <p className="text-xl font-medium text-gray-500 mb-2">Ask anything about your data</p>
              <div className="flex flex-wrap gap-2 justify-center max-w-lg mx-auto">
                {['Show total sales by category', 'What are the top 10 products?', 'Average revenue per month'].map((q) => (
                  <button
                    key={q}
                    onClick={() => setQuestion(q)}
                    className="px-3 py-1.5 text-sm bg-gray-800/50 border border-gray-700/50 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-gray-800 transition-all"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {conversations.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-2xl ${msg.role === 'user'
                ? 'bg-brand-600 rounded-2xl rounded-tr-md px-5 py-3'
                : 'glass-card p-5 w-full'
              }`}>
                {msg.role === 'user' ? (
                  <p>{msg.content}</p>
                ) : msg.error ? (
                  <p className="text-red-400">{msg.error}</p>
                ) : (
                  <div className="space-y-4">
                    {/* SQL */}
                    <details className="group">
                      <summary className="flex items-center gap-2 text-sm text-gray-400 cursor-pointer hover:text-gray-300">
                        <Code2 className="w-4 h-4" />
                        Generated SQL
                      </summary>
                      <pre className="mt-2 p-3 bg-gray-800/50 rounded-lg text-sm text-green-400 overflow-x-auto font-mono">
                        {msg.data.generated_sql}
                      </pre>
                    </details>

                    {/* Chart */}
                    {msg.data.chart_type && msg.data.chart_type !== 'table' && (
                      <ChartRenderer type={msg.data.chart_type} config={msg.data.chart_config} />
                    )}

                    {/* Results table */}
                    {msg.data.results?.length > 0 && (
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b border-gray-700">
                              {msg.data.columns?.map((col) => (
                                <th key={col} className="text-left p-2 text-gray-400 font-medium">{col}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {msg.data.results.slice(0, 10).map((row, ri) => (
                              <tr key={ri} className="border-b border-gray-800/50">
                                {msg.data.columns?.map((col) => (
                                  <td key={col} className="p-2 text-gray-300">{row[col]}</td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}

                    {/* Metrics */}
                    <div className="flex gap-4 text-xs text-gray-500">
                      <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {msg.data.execution_time_ms}ms</span>
                      <span>{msg.data.row_count} rows</span>
                      <span className="text-brand-400/70">{msg.data.chart_type}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="glass-card px-5 py-4 flex items-center gap-3">
                <Loader2 className="w-5 h-5 animate-spin text-brand-400" />
                <span className="text-gray-400">Generating SQL and querying data...</span>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input */}
        <form onSubmit={handleSubmit} className="glass-card p-4 flex gap-3">
          <input
            id="chat-input"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder={selectedDataset ? 'Ask a question about your data...' : 'Select a dataset first...'}
            disabled={!selectedDataset}
            className="input-field flex-1"
          />
          <button
            id="chat-submit"
            type="submit"
            disabled={!question.trim() || !selectedDataset || loading}
            className="btn-primary px-4"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>

      {/* Right sidebar */}
      <div className="w-72 hidden xl:flex flex-col gap-4 overflow-auto">
        <DatasetBrowser datasets={datasets} selectedId={selectedDataset} onSelect={setSelectedDataset} />
        <QueryHistory queries={history} />
      </div>
    </div>
  )
}
