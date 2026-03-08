import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { contentAPI } from '../../services/api'
import { useAuth } from '../../context/AuthContext'

function StatCard({ icon, label, value }) {
  return (
    <div className="card flex items-center gap-4">
      <div className="text-4xl">{icon}</div>
      <div>
        <p className="text-2xl font-bold text-slate-800">{value}</p>
        <p className="text-sm text-slate-500">{label}</p>
      </div>
    </div>
  )
}

function DifficultyBadge({ level }) {
  const colours = {
    beginner:     'bg-green-100 text-green-700',
    intermediate: 'bg-amber-100 text-amber-700',
    advanced:     'bg-red-100  text-red-700',
  }
  return (
    <span className={`badge ${colours[level] || 'bg-slate-100 text-slate-600'}`}>
      {level}
    </span>
  )
}

export default function Dashboard() {
  const { user } = useAuth()
  const [recent,  setRecent]  = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    contentAPI
      .getHistory()
      .then((data) => setRecent(data.history.slice(0, 5)))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 animate-slide-up">
      {/* Greeting */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-800">
          Welcome back, {user?.name?.split(' ')[0]} 👋
        </h1>
        <p className="text-slate-500 mt-1">
          Ready to learn something new today? Enter any topic and let AI build your module.
        </p>
      </div>

      {/* Quick action */}
      <div className="bg-gradient-to-r from-indigo-600 to-violet-600 rounded-2xl p-6 text-white mb-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">Generate a Learning Module</h2>
          <p className="text-indigo-200 text-sm mt-1">
            Text · Images · Voice narration — all in one place.
          </p>
        </div>
        <Link
          to="/generate"
          className="bg-white text-indigo-700 font-semibold px-5 py-2.5 rounded-lg hover:bg-indigo-50 transition whitespace-nowrap"
        >
          Start Generating ✨
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <StatCard icon="📖" label="Modules Generated" value={recent.length > 0 ? recent.length + '+' : '0'} />
        <StatCard icon="🧠" label="Topics Explored"   value={new Set(recent.map((r) => r.topic)).size} />
        <StatCard icon="⚡" label="AI-Powered"        value="100%" />
      </div>

      {/* Recent modules */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-800">Recent Modules</h2>
          <Link to="/history" className="text-sm text-indigo-600 hover:underline">
            View all →
          </Link>
        </div>

        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="card animate-pulse h-16 bg-slate-100" />
            ))}
          </div>
        ) : recent.length === 0 ? (
          <div className="card text-center py-10 text-slate-400">
            <p className="text-4xl mb-2">📭</p>
            <p>No modules yet. Generate your first one!</p>
            <Link to="/generate" className="btn-primary inline-block mt-4">
              Generate Now
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {recent.map((item) => (
              <Link
                key={item.id}
                to={`/module/${item.id}`}
                className="card flex items-center justify-between hover:shadow-md transition-shadow group"
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">📄</span>
                  <div>
                    <p className="font-medium text-slate-800 group-hover:text-indigo-600 transition-colors">
                      {item.topic}
                    </p>
                    <p className="text-xs text-slate-400">
                      {new Date(item.created_at).toLocaleDateString('en-GB', {
                        day: 'numeric', month: 'short', year: 'numeric',
                      })}
                    </p>
                  </div>
                </div>
                <DifficultyBadge level={item.difficulty_level} />
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
