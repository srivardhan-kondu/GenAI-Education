import React, { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const NAV_LINKS = [
    { to: '/', label: 'Dashboard', icon: '🏠' },
    { to: '/generate', label: 'Generate', icon: '✨' },
    { to: '/history', label: 'History', icon: '📚' },
    { to: '/search', label: 'Search', icon: '🔍' },
]

export default function Navbar() {
    const { user, logout } = useAuth()
    const navigate = useNavigate()
    const [mobileOpen, setMobileOpen] = useState(false)

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    return (
        <nav className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200">
            <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
                {/* Logo */}
                <Link to="/" className="flex items-center gap-2 group">
                    <span className="text-2xl">🎓</span>
                    <span className="text-lg font-bold text-slate-800 group-hover:text-indigo-600 transition-colors">
                        EduGen AI
                    </span>
                </Link>

                {/* Desktop nav links */}
                <div className="hidden md:flex items-center gap-1">
                    {NAV_LINKS.map((link) => (
                        <NavLink
                            key={link.to}
                            to={link.to}
                            end={link.to === '/'}
                            className={({ isActive }) =>
                                `px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${isActive
                                    ? 'bg-indigo-50 text-indigo-700'
                                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-800'
                                }`
                            }
                        >
                            {link.icon} {link.label}
                        </NavLink>
                    ))}
                </div>

                {/* User area (desktop) */}
                <div className="hidden md:flex items-center gap-3">
                    <Link
                        to="/profile"
                        className="flex items-center gap-2 text-sm text-slate-600 hover:text-indigo-600 transition-colors"
                    >
                        <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-bold text-xs">
                            {user?.name?.charAt(0)?.toUpperCase() || '?'}
                        </div>
                        <span className="font-medium max-w-[120px] truncate">{user?.name}</span>
                    </Link>
                    <button
                        onClick={handleLogout}
                        className="text-sm text-slate-500 hover:text-red-600 transition-colors px-2 py-1"
                    >
                        Logout
                    </button>
                </div>

                {/* Mobile hamburger */}
                <button
                    onClick={() => setMobileOpen(!mobileOpen)}
                    className="md:hidden p-2 rounded-lg hover:bg-slate-100 transition-colors"
                    aria-label="Toggle menu"
                >
                    <svg className="w-5 h-5 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        {mobileOpen ? (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        ) : (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                        )}
                    </svg>
                </button>
            </div>

            {/* Mobile menu */}
            {mobileOpen && (
                <div className="md:hidden border-t border-slate-200 bg-white animate-slide-up">
                    <div className="px-4 py-3 space-y-1">
                        {NAV_LINKS.map((link) => (
                            <NavLink
                                key={link.to}
                                to={link.to}
                                end={link.to === '/'}
                                onClick={() => setMobileOpen(false)}
                                className={({ isActive }) =>
                                    `block px-3 py-2 rounded-lg text-sm font-medium transition-colors ${isActive
                                        ? 'bg-indigo-50 text-indigo-700'
                                        : 'text-slate-600 hover:bg-slate-100'
                                    }`
                                }
                            >
                                {link.icon} {link.label}
                            </NavLink>
                        ))}
                        <hr className="my-2 border-slate-200" />
                        <Link
                            to="/profile"
                            onClick={() => setMobileOpen(false)}
                            className="block px-3 py-2 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-100"
                        >
                            👤 Profile
                        </Link>
                        <button
                            onClick={handleLogout}
                            className="w-full text-left px-3 py-2 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50"
                        >
                            🚪 Logout
                        </button>
                    </div>
                </div>
            )}
        </nav>
    )
}
