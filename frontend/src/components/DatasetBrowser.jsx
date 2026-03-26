import React from 'react'
import { Database, FileSpreadsheet } from 'lucide-react'

export default function DatasetBrowser({ datasets, selectedId, onSelect }) {
  return (
    <div className="glass-card p-4">
      <h3 className="text-sm font-semibold text-gray-400 mb-3 flex items-center gap-2">
        <Database className="w-4 h-4" /> Datasets
      </h3>
      {datasets.length === 0 ? (
        <p className="text-xs text-gray-600 text-center py-4">No datasets</p>
      ) : (
        <div className="space-y-1">
          {datasets.map((ds) => (
            <button
              key={ds.dataset_id}
              onClick={() => onSelect(ds.dataset_id)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all ${
                selectedId === ds.dataset_id
                  ? 'bg-brand-600/20 text-brand-400 border border-brand-500/20'
                  : 'text-gray-400 hover:bg-gray-800/50 hover:text-gray-300'
              }`}
            >
              <div className="flex items-center gap-2">
                <FileSpreadsheet className="w-3.5 h-3.5 flex-shrink-0" />
                <span className="truncate">{ds.name}</span>
              </div>
              <p className="text-xs text-gray-600 ml-5.5 mt-0.5">
                {ds.row_count?.toLocaleString()} rows
              </p>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
