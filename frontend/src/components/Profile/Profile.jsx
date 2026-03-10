import React, { useState } from 'react'
import toast from 'react-hot-toast'
import { useAuth } from '../../context/AuthContext'
import { authAPI } from '../../services/api'

const DIFFICULTY_OPTIONS = ['beginner', 'intermediate', 'advanced']
const STYLE_OPTIONS = ['short', 'detailed']

export default function Profile() {
    const { user, updateUser } = useAuth()

    const [form, setForm] = useState({
        name: user?.name || '',
        difficulty_level: user?.preferences?.difficulty_level || 'beginner',
        explanation_style: user?.preferences?.explanation_style || 'detailed',
        visual_learning: user?.preferences?.visual_learning ?? true,
    })
    const [saving, setSaving] = useState(false)

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target
        setForm((prev) => ({ ...prev, [name]: type === 'checkbox' ? checked : value }))
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setSaving(true)
        try {
            const payload = {
                name: form.name,
                preferences: {
                    difficulty_level: form.difficulty_level,
                    explanation_style: form.explanation_style,
                    visual_learning: form.visual_learning,
                },
            }
            const updated = await authAPI.updateProfile(payload)
            updateUser(updated)
            toast.success('Profile updated!')
        } catch (err) {
            toast.error(err.message)
        } finally {
            setSaving(false)
        }
    }

    return (
        <div className="max-w-xl mx-auto px-4 py-8 animate-slide-up">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-slate-800">Your Profile</h1>
                <p className="text-slate-500 mt-1">Update your details and learning preferences.</p>
            </div>

            <div className="card">
                {/* Avatar */}
                <div className="flex items-center gap-4 mb-6 pb-6 border-b border-slate-100">
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-white text-2xl font-bold shadow-md">
                        {user?.name?.charAt(0)?.toUpperCase() || '?'}
                    </div>
                    <div>
                        <p className="font-semibold text-lg text-slate-800">{user?.name}</p>
                        <p className="text-sm text-slate-500">{user?.email}</p>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">
                    {/* Name */}
                    <div>
                        <label className="label" htmlFor="name">Full name</label>
                        <input
                            id="name"
                            name="name"
                            type="text"
                            required
                            minLength={2}
                            value={form.name}
                            onChange={handleChange}
                            className="input-field"
                        />
                    </div>

                    {/* Difficulty */}
                    <div>
                        <label className="label" htmlFor="difficulty_level">Default difficulty level</label>
                        <select
                            id="difficulty_level"
                            name="difficulty_level"
                            value={form.difficulty_level}
                            onChange={handleChange}
                            className="input-field"
                        >
                            {DIFFICULTY_OPTIONS.map((opt) => (
                                <option key={opt} value={opt}>
                                    {opt.charAt(0).toUpperCase() + opt.slice(1)}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Explanation style */}
                    <div>
                        <label className="label" htmlFor="explanation_style">Explanation style</label>
                        <select
                            id="explanation_style"
                            name="explanation_style"
                            value={form.explanation_style}
                            onChange={handleChange}
                            className="input-field"
                        >
                            {STYLE_OPTIONS.map((opt) => (
                                <option key={opt} value={opt}>
                                    {opt.charAt(0).toUpperCase() + opt.slice(1)}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Visual learning */}
                    <div className="flex items-center gap-3">
                        <input
                            id="visual_learning"
                            name="visual_learning"
                            type="checkbox"
                            checked={form.visual_learning}
                            onChange={handleChange}
                            className="w-4 h-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                        />
                        <label htmlFor="visual_learning" className="text-sm font-medium text-slate-700">
                            Generate visual diagrams by default
                        </label>
                    </div>

                    {/* Submit */}
                    <button
                        type="submit"
                        disabled={saving}
                        className="btn-primary w-full flex items-center justify-center gap-2"
                    >
                        {saving ? (
                            <>
                                <span className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                                Saving…
                            </>
                        ) : (
                            'Save Changes'
                        )}
                    </button>
                </form>
            </div>
        </div>
    )
}
