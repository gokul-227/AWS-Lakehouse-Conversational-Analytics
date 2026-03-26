import React from 'react'
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'

const COLORS = ['#6366f1', '#8b5cf6', '#a78bfa', '#c4b5fd', '#818cf8', '#6d28d9', '#7c3aed', '#4f46e5']

export default function ChartRenderer({ type, config }) {
  if (!config || !config.data || config.data.length === 0) return null

  const commonProps = {
    width: '100%',
    height: 280,
  }

  if (type === 'metric') {
    return (
      <div className="text-center py-6">
        <p className="text-4xl font-bold gradient-text">{config.value}</p>
        <p className="text-sm text-gray-400 mt-2">{config.title}</p>
      </div>
    )
  }

  if (type === 'bar') {
    return (
      <ResponsiveContainer {...commonProps}>
        <BarChart data={config.data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey={config.xKey} tick={{ fill: '#9ca3af', fontSize: 12 }} />
          <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} />
          <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#f3f4f6' }} />
          <Legend />
          {config.yKeys?.map((key, i) => (
            <Bar key={key} dataKey={key} fill={COLORS[i % COLORS.length]} radius={[4, 4, 0, 0]} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    )
  }

  if (type === 'line') {
    return (
      <ResponsiveContainer {...commonProps}>
        <LineChart data={config.data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey={config.xKey} tick={{ fill: '#9ca3af', fontSize: 12 }} />
          <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} />
          <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#f3f4f6' }} />
          <Legend />
          {config.yKeys?.map((key, i) => (
            <Line key={key} type="monotone" dataKey={key} stroke={COLORS[i % COLORS.length]} strokeWidth={2} dot={false} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    )
  }

  if (type === 'pie') {
    return (
      <ResponsiveContainer {...commonProps}>
        <PieChart>
          <Pie
            data={config.data}
            dataKey={config.valueKey}
            nameKey={config.nameKey}
            cx="50%" cy="50%"
            outerRadius={100}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          >
            {config.data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#f3f4f6' }} />
        </PieChart>
      </ResponsiveContainer>
    )
  }

  return null
}
