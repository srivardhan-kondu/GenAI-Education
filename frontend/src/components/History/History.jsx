import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { contentAPI } from '../../services/api'
import toast from 'react-hot-toast'

const DIFFICULTY_COLOURS = {
  beginner:     'bg-green-100 text-green-700',
  intermediate: 'bg-amber-100 text-amber-700',
  advanced:     'bg-red-100  text-red-700',
}

export default function History() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    contentAPI
      .getHistory()
      .then((data) => setHistory(data.history))
      .catch(() => toast.error('Could not load history.'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 animate-slide-up">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-800">Learning History</h1>
          <p className="text-slate-500 mt-1">All your generated learning modules.</p>
        </div>
        <Link to="/generate" className="btn-primary text-sm">
          + New Module
        </Link>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="card h-20 animate-pulse bg-slate-100" />
          ))}
        </div>
      ) : history.length === 0 ? (
        <div className="card text-center py-16 text-slate-400">
          <p className="text-5xl mb-3">📭</p>
          <p className="text-lg font-medium">No modules yet.</p>
          <p className="text-sm mb-6">Generate your first learning module to get started.</p>
          <Link to="/generate" className="btn-primary inline-block">
            Generate Now
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {history.map((item, idx) => (
            <Link
              key={item.id}
              to={`/module/${item.id}`}
              className="card flex items-center justify-between hover:shadow-md transition-shadow group"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-indigo-100 flex items-center justify-center text-indigo-700 font-bold text-sm flex-shrink-0">
                  {idx + 1}
                </div>
                <div>
                  <p className="font-semibold text-slate-800 group-hover:text-indigo-600 transition-colors">
                    {item.topic}
                  </p>
                  <p className="text-xs text-slate-400">
                    {new Date(item.created_at).toLocaleDateString('en-GB', {
                      weekday: 'short', day: 'numeric', month: 'short', year: 'numeric',
                    })}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className={`badge ${DIFFICULTY_COLOURS[item.difficulty_level] || 'bg-slate-100 text-slate-600'}`}>
                  {item.difficulty_level}
                </span>
                <span className="text-slate-400 group-hover:text-indigo-600 transition-colors text-lg">→</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
