import React, { useState } from 'react'
import toast from 'react-hot-toast'
import { notesAPI } from '../../services/api'

const FORMAT_OPTIONS = [
    { id: 'structured', label: '📄 Study Notes', desc: 'Clean structured notes from your module' },
    { id: 'cornell', label: '📝 Cornell Notes', desc: 'AI-generated Cues + Notes + Summary' },
    { id: 'flashcards', label: '🃏 Flashcards', desc: 'AI-generated Q&A flashcards' },
]

export default function NotesPanel({ moduleId, topic }) {
    const [format, setFormat] = useState('structured')
    const [notes, setNotes] = useState(null)
    const [loading, setLoading] = useState(false)
    const [downloading, setDL] = useState(false)

    const handleGenerate = async () => {
        setLoading(true)
        setNotes(null)
        try {
            const data = await notesAPI.getNotes(moduleId, format)
            setNotes(data)
        } catch (err) {
            toast.error(err.message)
        } finally {
            setLoading(false)
        }
    }

    const handleDownload = async () => {
        setDL(true)
        try {
            await notesAPI.downloadPDF(moduleId, format)
            toast.success('PDF downloaded!')
        } catch (err) {
            toast.error('Download failed — ' + err.message)
        } finally {
            setDL(false)
        }
    }

    return (
        <div className="space-y-6 animate-slide-up">
            {/* Format picker */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {FORMAT_OPTIONS.map((opt) => (
                    <button
                        key={opt.id}
                        onClick={() => { setFormat(opt.id); setNotes(null) }}
                        className={`card text-left transition-all !p-4 cursor-pointer ${format === opt.id
                                ? 'ring-2 ring-indigo-500 bg-indigo-50'
                                : 'hover:shadow-md'
                            }`}
                    >
                        <p className="font-semibold text-slate-800 text-sm">{opt.label}</p>
                        <p className="text-xs text-slate-500 mt-1">{opt.desc}</p>
                    </button>
                ))}
            </div>

            {/* Actions */}
            <div className="flex gap-3">
                <button
                    onClick={handleGenerate}
                    disabled={loading}
                    className="btn-primary flex items-center gap-2"
                >
                    {loading ? (
                        <>
                            <span className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                            Generating…
                        </>
                    ) : (
                        '🧠 Generate Notes'
                    )}
                </button>

                {notes && (
                    <button
                        onClick={handleDownload}
                        disabled={downloading}
                        className="btn-secondary flex items-center gap-2"
                    >
                        {downloading ? (
                            <>
                                <span className="animate-spin h-4 w-4 border-2 border-indigo-600 border-t-transparent rounded-full" />
                                Downloading…
                            </>
                        ) : (
                            '📥 Download PDF'
                        )}
                    </button>
                )}
            </div>

            {/* Notes display */}
            {notes && notes.type === 'structured' && <StructuredView notes={notes} />}
            {notes && notes.type === 'cornell' && <CornellView notes={notes} />}
            {notes && notes.type === 'flashcards' && <FlashcardsView notes={notes} />}
        </div>
    )
}


// ── Structured Notes View ───────────────────────────────────────────────────
function StructuredView({ notes }) {
    return (
        <div className="card space-y-5">
            <h2 className="text-xl font-bold text-slate-800">{notes.topic}</h2>
            {notes.sections?.map((section, i) => (
                <div key={i}>
                    <h3 className="font-semibold text-indigo-600 mb-2">{section.heading}</h3>
                    {section.content && (
                        <p className="text-slate-700 text-sm leading-relaxed">{section.content}</p>
                    )}
                    {section.items?.length > 0 && (
                        <ol className="list-decimal list-inside text-sm text-slate-700 space-y-1 ml-2">
                            {section.items.map((item, j) => (
                                <li key={j}>{item}</li>
                            ))}
                        </ol>
                    )}
                </div>
            ))}
        </div>
    )
}


// ── Cornell Notes View ──────────────────────────────────────────────────────
function CornellView({ notes }) {
    return (
        <div className="card">
            <h2 className="text-xl font-bold text-slate-800 mb-4">
                📝 Cornell Notes — {notes.topic}
            </h2>

            {/* Two-column layout */}
            <div className="border border-slate-200 rounded-xl overflow-hidden">
                {/* Header */}
                <div className="grid grid-cols-[35%_1fr] bg-indigo-50 font-semibold text-sm text-indigo-800">
                    <div className="px-4 py-2 border-r border-slate-200">Cue / Question</div>
                    <div className="px-4 py-2">Notes</div>
                </div>

                {/* Rows */}
                {notes.cue_column?.map((pair, i) => (
                    <div
                        key={i}
                        className={`grid grid-cols-[35%_1fr] text-sm ${i % 2 === 0 ? 'bg-white' : 'bg-slate-50'
                            }`}
                    >
                        <div className="px-4 py-3 border-r border-slate-200 font-medium text-indigo-700">
                            {pair.cue}
                        </div>
                        <div className="px-4 py-3 text-slate-700 leading-relaxed">
                            {pair.notes}
                        </div>
                    </div>
                ))}
            </div>

            {/* Summary */}
            {notes.summary && (
                <div className="mt-4 p-4 bg-slate-50 rounded-xl border border-slate-200">
                    <p className="font-semibold text-sm text-indigo-700 mb-1">📌 Summary</p>
                    <p className="text-sm text-slate-700 leading-relaxed">{notes.summary}</p>
                </div>
            )}
        </div>
    )
}


// ── Flashcards View ─────────────────────────────────────────────────────────
function FlashcardsView({ notes }) {
    const [flipped, setFlipped] = useState({})

    const toggleFlip = (idx) =>
        setFlipped((prev) => ({ ...prev, [idx]: !prev[idx] }))

    return (
        <div className="space-y-3">
            <h2 className="text-xl font-bold text-slate-800 mb-2">
                🃏 Flashcards — {notes.topic}
            </h2>
            <p className="text-sm text-slate-500 mb-4">Click a card to reveal the answer.</p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {notes.flashcards?.map((card, i) => (
                    <button
                        key={i}
                        onClick={() => toggleFlip(i)}
                        className={`card text-left transition-all min-h-[120px] cursor-pointer ${flipped[i]
                                ? 'bg-indigo-50 ring-2 ring-indigo-300'
                                : 'hover:shadow-md'
                            }`}
                    >
                        <p className="text-xs text-slate-400 mb-2">Card {i + 1}</p>
                        {!flipped[i] ? (
                            <p className="font-semibold text-slate-800 text-sm">
                                ❓ {card.question}
                            </p>
                        ) : (
                            <p className="text-sm text-indigo-800 leading-relaxed">
                                ✅ {card.answer}
                            </p>
                        )}
                        <p className="text-xs text-slate-400 mt-3">
                            {flipped[i] ? 'Click to see question' : 'Click to reveal answer'}
                        </p>
                    </button>
                ))}
            </div>
        </div>
    )
}
