import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { listDatasets, getQueryHistory } from '../services/api'
import { Database, MessageSquare, Upload, Clock, FileSpreadsheet, TrendingUp } from 'lucide-react'

export default function DashboardPage() {
  const [datasets, setDatasets] = useState([])
  const [queries, setQueries] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const [dsRes, qRes] = await Promise.all([listDatasets(), getQueryHistory()])
        setDatasets(dsRes.datasets || [])
        setQueries(qRes.queries || [])
      } catch (err) {
        console.log('API not available — showing empty dashboard')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const stats = [
    { label: 'Datasets', value: datasets.length, icon: Database, color: 'from-brand-500 to-blue-500' },
    { label: 'Queries', value: queries.length, icon: MessageSquare, color: 'from-purple-500 to-pink-500' },
    { label: 'Total Rows', value: datasets.reduce((s, d) => s + (d.row_count || 0), 0).toLocaleString(), icon: FileSpreadsheet, color: 'from-green-500 to-emerald-500' },
    { label: 'Avg Response', value: queries.length ? `${Math.round(queries.reduce((s, q) => s + (q.execution_time_ms || 0), 0) / queries.length)}ms` : '—', icon: TrendingUp, color: 'from-orange-500 to-amber-500' },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
        <p className="text-gray-400">Your data lake at a glance</p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="glass-card p-6">
            <div className="flex items-center justify-between mb-4">
              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center`}>
                <Icon className="w-5 h-5 text-white" />
              </div>
            </div>
            <p className="text-2xl font-bold">{loading ? '—' : value}</p>
            <p className="text-sm text-gray-400">{label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent datasets */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Recent Datasets</h2>
            <Link to="/upload" className="text-sm text-brand-400 hover:text-brand-300 flex items-center gap-1">
              <Upload className="w-4 h-4" /> Upload
            </Link>
          </div>
          {datasets.length === 0 ? (
            <div className="text-center py-8">
              <Database className="w-12 h-12 text-gray-700 mx-auto mb-3" />
              <p className="text-gray-500">No datasets yet</p>
              <Link to="/upload" className="text-brand-400 text-sm hover:underline">Upload your first dataset</Link>
            </div>
          ) : (
            <div className="space-y-3">
              {datasets.slice(0, 5).map((ds) => (
                <div key={ds.dataset_id} className="flex items-center justify-between p-3 bg-gray-800/30 rounded-xl">
                  <div className="flex items-center gap-3">
                    <FileSpreadsheet className="w-5 h-5 text-brand-400" />
                    <div>
                      <p className="text-sm font-medium">{ds.name}</p>
                      <p className="text-xs text-gray-500">{ds.row_count?.toLocaleString()} rows · {ds.file_type?.toUpperCase()}</p>
                    </div>
                  </div>
                  <Link to={`/chat/${ds.dataset_id}`} className="text-xs text-brand-400 hover:text-brand-300">
                    Query →
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent queries */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Recent Queries</h2>
            <Link to="/chat" className="text-sm text-brand-400 hover:text-brand-300 flex items-center gap-1">
              <MessageSquare className="w-4 h-4" /> Chat
            </Link>
          </div>
          {queries.length === 0 ? (
            <div className="text-center py-8">
              <Clock className="w-12 h-12 text-gray-700 mx-auto mb-3" />
              <p className="text-gray-500">No queries yet</p>
              <Link to="/chat" className="text-brand-400 text-sm hover:underline">Ask your first question</Link>
            </div>
          ) : (
            <div className="space-y-3">
              {queries.slice(0, 5).map((q) => (
                <div key={q.query_id} className="p-3 bg-gray-800/30 rounded-xl">
                  <p className="text-sm font-medium mb-1">{q.question}</p>
                  <div className="flex items-center gap-3 text-xs text-gray-500">
                    <span>{q.row_count} results</span>
                    <span>{q.execution_time_ms}ms</span>
                    <span className="text-brand-400/70">{q.chart_type}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
