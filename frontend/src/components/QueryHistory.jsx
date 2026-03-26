import React from 'react'
import { Clock } from 'lucide-react'

export default function QueryHistory({ queries }) {
  return (
    <div className="glass-card p-4">
      <h3 className="text-sm font-semibold text-gray-400 mb-3 flex items-center gap-2">
        <Clock className="w-4 h-4" /> Recent Queries
      </h3>
      {queries.length === 0 ? (
        <p className="text-xs text-gray-600 text-center py-4">No history</p>
      ) : (
        <div className="space-y-2">
          {queries.slice(0, 8).map((q) => (
            <div key={q.query_id} className="p-2 bg-gray-800/30 rounded-lg">
              <p className="text-xs text-gray-300 line-clamp-2">{q.question}</p>
              <div className="flex gap-2 mt-1 text-xs text-gray-600">
                <span>{q.execution_time_ms}ms</span>
                <span>{q.row_count} rows</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
