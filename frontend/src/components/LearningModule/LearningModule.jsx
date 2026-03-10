import React, { useEffect, useState } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import { contentAPI } from '../../services/api'
import TextContent from './TextContent'
import ImageContent from './ImageContent'
import AudioContent from './AudioContent'
import VideoContent from './VideoContent'
import NotesPanel from './NotesPanel'

const DIFFICULTY_COLOURS = {
  beginner: 'bg-green-100 text-green-700',
  intermediate: 'bg-amber-100 text-amber-700',
  advanced: 'bg-red-100  text-red-700',
}

export default function LearningModule() {
  const { id } = useParams()
  const { state } = useLocation()
  const navigate = useNavigate()
  const [module, setModule] = useState(state?.module || null)
  const [loading, setLoading] = useState(!state?.module)
  const [activeTab, setTab] = useState('text')

  useEffect(() => {
    if (!module) {
      contentAPI
        .getModule(id)
        .then(setModule)
        .catch(() => {
          toast.error('Could not load module.')
          navigate('/history')
        })
        .finally(() => setLoading(false))
    }
  }, [id]) // eslint-disable-line

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-4 border-indigo-600 border-t-transparent rounded-full mx-auto" />
          <p className="mt-4 text-slate-500">Loading module…</p>
        </div>
      </div>
    )
  }

  if (!module) return null

  const tabs = [
    { id: 'text', label: '📖 Content', always: true },
    { id: 'images', label: '🖼 Images', always: false, hidden: !module.images?.some(i => i.base64_data) },
    { id: 'video', label: '🎬 Video', always: false, hidden: !module.videos?.some(v => v.base64_data) },
    { id: 'audio', label: '🔊 Audio', always: false, hidden: !module.audio_base64 },
    { id: 'notes', label: '📝 Notes', always: true },
  ].filter((t) => !t.hidden)

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 animate-slide-up">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <button
            onClick={() => navigate(-1)}
            className="text-sm text-slate-500 hover:text-slate-800 flex items-center gap-1"
          >
            ← Back
          </button>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h1 className="text-3xl font-bold text-slate-800">{module.topic}</h1>
            <p className="text-slate-400 text-sm mt-1">
              Generated on {new Date(module.created_at).toLocaleDateString('en-GB', {
                day: 'numeric', month: 'long', year: 'numeric',
              })}
            </p>
          </div>
          <span className={`badge text-sm px-3 py-1 ${DIFFICULTY_COLOURS[module.difficulty_level] || 'bg-slate-100 text-slate-600'}`}>
            {module.difficulty_level}
          </span>
        </div>

        {/* Concept tags */}
        {module.concepts?.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {module.concepts.map((c) => (
              <span key={c} className="badge bg-indigo-100 text-indigo-700">
                🏷 {c}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Tabs */}
      {tabs.length > 1 && (
        <div className="flex gap-1 bg-slate-100 p-1 rounded-xl mb-6 w-fit">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setTab(tab.id)}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all
                ${activeTab === tab.id
                  ? 'bg-white text-indigo-700 shadow-sm'
                  : 'text-slate-600 hover:text-slate-800'}`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      )}

      {/* Tab content */}
      {activeTab === 'text' && (
        <TextContent
          definition={module.definition}
          explanation={module.explanation}
          examples={module.examples}
          keyPoints={module.key_points}
          summary={module.summary}
        />
      )}
      {activeTab === 'images' && (
        <ImageContent images={module.images} />
      )}
      {activeTab === 'video' && (
        <VideoContent videos={module.videos} />
      )}
      {activeTab === 'audio' && (
        <AudioContent audioBase64={module.audio_base64} />
      )}
      {activeTab === 'notes' && (
        <NotesPanel moduleId={module.id} topic={module.topic} />
      )}

      {/* If only one tab, show all sections inline */}
      {tabs.length === 1 && (
        <>
          <ImageContent images={module.images} />
          <div className="mt-6">
            <AudioContent audioBase64={module.audio_base64} />
          </div>
        </>
      )}
    </div>
  )
}
