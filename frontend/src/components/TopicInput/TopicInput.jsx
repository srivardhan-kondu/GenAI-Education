import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { contentAPI } from '../../services/api'

const DIFFICULTY_OPTIONS = [
  { value: 'beginner',     label: 'Beginner',     desc: 'Simple language, analogies',   icon: '🌱' },
  { value: 'intermediate', label: 'Intermediate', desc: 'Some technical depth',          icon: '🌿' },
  { value: 'advanced',     label: 'Advanced',     desc: 'Full technical precision',      icon: '🌳' },
]

const STYLE_OPTIONS = [
  { value: 'detailed', label: 'Detailed', desc: 'Thorough explanations' },
  { value: 'short',    label: 'Short',    desc: 'Concise & quick read' },
]

const STEPS = [
  { label: 'Generating educational text…',      pct: 15 },
  { label: 'Extracting key concepts…',          pct: 35 },
  { label: 'Creating visual diagrams…',         pct: 60 },
  { label: 'Recording voice narration…',        pct: 80 },
  { label: 'Assembling learning module…',       pct: 95 },
]

export default function TopicInput() {
  const navigate = useNavigate()

  const [topic,          setTopic]          = useState('')
  const [difficulty,     setDifficulty]     = useState('beginner')
  const [style,          setStyle]          = useState('detailed')
  const [genImages,      setGenImages]      = useState(true)
  const [genAudio,       setGenAudio]       = useState(true)
  const [loading,        setLoading]        = useState(false)
  const [stepIdx,        setStepIdx]        = useState(0)
  const [progress,       setProgress]       = useState(0)

  // Simulate step-by-step progress while waiting for API
  const startProgressSim = () => {
    let idx = 0
    const tick = () => {
      if (idx < STEPS.length) {
        setStepIdx(idx)
        setProgress(STEPS[idx].pct)
        idx++
        setTimeout(tick, idx === 0 ? 800 : 2200)
      }
    }
    tick()
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!topic.trim()) {
      toast.error('Please enter a topic.')
      return
    }

    setLoading(true)
    setProgress(5)
    startProgressSim()

    try {
      const data = await contentAPI.generate({
        topic:             topic.trim(),
        difficulty_level:  difficulty,
        explanation_style: style,
        generate_images:   genImages,
        generate_audio:    genAudio,
      })
      setProgress(100)
      toast.success('Learning module ready!')
      navigate(`/module/${data.id}`, { state: { module: data } })
    } catch (err) {
      toast.error(err.message)
      setLoading(false)
      setProgress(0)
      setStepIdx(0)
    }
  }

  const exampleTopics = [
    'Binary Search', 'Photosynthesis', 'Neural Networks',
    'The Solar System', 'Newton\'s Laws', 'DNA Replication',
  ]

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 animate-slide-up">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-800">Generate Learning Module</h1>
        <p className="text-slate-500 mt-1">
          Enter any topic and our AI will create text, images, and voice narration for you.
        </p>
      </div>

      {loading ? (
        /* ── Progress Screen ─────────────────────────────────────────────── */
        <div className="card text-center py-12">
          <div className="text-5xl mb-4 animate-bounce">🤖</div>
          <h2 className="text-xl font-bold text-slate-800 mb-1">AI is working…</h2>
          <p className="text-slate-500 text-sm mb-6">{STEPS[stepIdx]?.label}</p>

          {/* Progress bar */}
          <div className="w-full bg-slate-200 rounded-full h-3 mb-3">
            <div
              className="bg-indigo-600 h-3 rounded-full transition-all duration-700 ease-in-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-xs text-slate-400">{progress}%</p>

          {/* Step indicators */}
          <div className="mt-8 space-y-2">
            {STEPS.map((s, i) => (
              <div key={i} className={`flex items-center gap-3 text-sm ${i <= stepIdx ? 'text-slate-700' : 'text-slate-300'}`}>
                <span className="text-base">
                  {i < stepIdx ? '✅' : i === stepIdx ? '⏳' : '⬜'}
                </span>
                {s.label}
              </div>
            ))}
          </div>
        </div>
      ) : (
        /* ── Input Form ──────────────────────────────────────────────────── */
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Topic input */}
          <div className="card">
            <label className="label text-base" htmlFor="topic">
              📌 Learning Topic
            </label>
            <input
              id="topic"
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="input-field text-base py-3"
              placeholder="e.g. Photosynthesis, Binary Search, Quantum Computing…"
              maxLength={200}
              required
            />
            {/* Example chips */}
            <div className="mt-3 flex flex-wrap gap-2">
              {exampleTopics.map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setTopic(t)}
                  className="text-xs bg-indigo-50 text-indigo-700 border border-indigo-200 px-3 py-1 rounded-full hover:bg-indigo-100 transition"
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* Difficulty */}
          <div className="card">
            <p className="label text-base mb-3">🎯 Difficulty Level</p>
            <div className="grid grid-cols-3 gap-3">
              {DIFFICULTY_OPTIONS.map(({ value, label, desc, icon }) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setDifficulty(value)}
                  className={`p-3 rounded-xl border-2 text-left transition-all
                    ${difficulty === value
                      ? 'border-indigo-500 bg-indigo-50'
                      : 'border-slate-200 hover:border-slate-300'}`}
                >
                  <div className="text-xl mb-1">{icon}</div>
                  <div className="font-semibold text-sm text-slate-800">{label}</div>
                  <div className="text-xs text-slate-500 mt-0.5">{desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Style */}
          <div className="card">
            <p className="label text-base mb-3">📝 Explanation Style</p>
            <div className="grid grid-cols-2 gap-3">
              {STYLE_OPTIONS.map(({ value, label, desc }) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setStyle(value)}
                  className={`p-3 rounded-xl border-2 text-left transition-all
                    ${style === value
                      ? 'border-indigo-500 bg-indigo-50'
                      : 'border-slate-200 hover:border-slate-300'}`}
                >
                  <div className="font-semibold text-sm text-slate-800">{label}</div>
                  <div className="text-xs text-slate-500 mt-0.5">{desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Media toggles */}
          <div className="card">
            <p className="label text-base mb-3">🎨 Include Media</p>
            <div className="space-y-3">
              {[
                { label: '🖼  AI-Generated Images', hint: 'Visual diagrams per concept', val: genImages, set: setGenImages },
                { label: '🔊 Voice Narration',       hint: 'Audio summary using ElevenLabs', val: genAudio, set: setGenAudio },
              ].map(({ label, hint, val, set }) => (
                <label key={label} className="flex items-center justify-between cursor-pointer">
                  <div>
                    <p className="text-sm font-medium text-slate-800">{label}</p>
                    <p className="text-xs text-slate-400">{hint}</p>
                  </div>
                  <div
                    onClick={() => set((v) => !v)}
                    className={`relative w-11 h-6 rounded-full transition-colors ${val ? 'bg-indigo-600' : 'bg-slate-300'}`}
                  >
                    <span
                      className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${val ? 'translate-x-5' : ''}`}
                    />
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Submit */}
          <button type="submit" className="btn-primary w-full text-base py-3">
            ✨ Generate Learning Module
          </button>
        </form>
      )}
    </div>
  )
}
