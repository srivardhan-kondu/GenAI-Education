import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { searchAPI } from '../../services/api'
import toast from 'react-hot-toast'

const DIFFICULTY_COLOURS = {
  beginner:     'bg-green-100 text-green-700',
  intermediate: 'bg-amber-100 text-amber-700',
  advanced:     'bg-red-100  text-red-700',
}

export default function Search() {
  const [query,   setQuery]   = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  const handleSearch = async (e) => {
    e.preventDefault()
    const q = query.trim()
    if (!q) return

    setLoading(true)
    setSearched(true)
    try {
      const data = await searchAPI.search(q)
      setResults(data.results)
    } catch (err) {
      toast.error(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 animate-slide-up">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-slate-800">Search Modules</h1>
        <p className="text-slate-500 mt-1">Find previously generated learning content by topic or keyword.</p>
      </div>

      {/* Search bar */}
      <form onSubmit={handleSearch} className="flex gap-2 mb-8">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by topic or concept…"
          className="input-field flex-1"
          maxLength={100}
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="btn-primary px-6 flex items-center gap-2"
        >
          {loading ? (
            <span className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
          ) : '🔍'}
        </button>
      </form>

      {/* Results */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card h-16 animate-pulse bg-slate-100" />
          ))}
        </div>
      ) : searched && results.length === 0 ? (
        <div className="card text-center py-12 text-slate-400">
          <p className="text-4xl mb-2">🔎</p>
          <p className="font-medium">No modules found for "{query}".</p>
          <p className="text-sm mt-1">Try a different keyword, or generate a new module.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {results.map((item) => (
            <Link
              key={item.id}
              to={`/module/${item.id}`}
              className="card flex items-center justify-between hover:shadow-md transition-shadow group"
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">📄</span>
                <div>
                  <p className="font-semibold text-slate-800 group-hover:text-indigo-600 transition-colors">
                    {item.topic}
                  </p>
                  <p className="text-xs text-slate-400">
                    {new Date(item.created_at).toLocaleDateString('en-GB', {
                      day: 'numeric', month: 'short', year: 'numeric',
                    })}
                  </p>
                </div>
              </div>
              <span className={`badge ${DIFFICULTY_COLOURS[item.difficulty_level] || 'bg-slate-100 text-slate-600'}`}>
                {item.difficulty_level}
              </span>
            </Link>
          ))}
        </div>
      )}

      {/* Not searched yet */}
      {!searched && (
        <div className="text-center text-slate-400 mt-4">
          <p className="text-3xl mb-2">🔍</p>
          <p>Enter a topic or keyword above to search your modules.</p>
        </div>
      )}
    </div>
  )
}
