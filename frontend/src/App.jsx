import React from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './context/AuthContext'

// Layout
import Navbar from './components/Navbar/Navbar'
import ProtectedRoute from './components/ProtectedRoute'

// Pages
import Login from './components/Auth/Login'
import Register from './components/Auth/Register'
import Dashboard from './components/Dashboard/Dashboard'
import TopicInput from './components/TopicInput/TopicInput'
import LearningModule from './components/LearningModule/LearningModule'
import History from './components/History/History'
import Search from './components/Search/Search'
import Profile from './components/Profile/Profile'

// ── Layout wrapper: shows Navbar on authenticated pages ─────────────────────
function AuthenticatedLayout({ children }) {
    return (
        <>
            <Navbar />
            <main>{children}</main>
        </>
    )
}

// ── Main routes ─────────────────────────────────────────────────────────────
function AppRoutes() {
    const { user, loading } = useAuth()

    // Redirect logged-in users away from auth pages
    const AuthRedirect = ({ children }) => {
        if (loading) return null
        if (user) return <Navigate to="/" replace />
        return children
    }

    return (
        <Routes>
            {/* Public */}
            <Route
                path="/login"
                element={
                    <AuthRedirect>
                        <Login />
                    </AuthRedirect>
                }
            />
            <Route
                path="/register"
                element={
                    <AuthRedirect>
                        <Register />
                    </AuthRedirect>
                }
            />

            {/* Protected */}
            <Route
                path="/"
                element={
                    <ProtectedRoute>
                        <AuthenticatedLayout><Dashboard /></AuthenticatedLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/generate"
                element={
                    <ProtectedRoute>
                        <AuthenticatedLayout><TopicInput /></AuthenticatedLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/module/:id"
                element={
                    <ProtectedRoute>
                        <AuthenticatedLayout><LearningModule /></AuthenticatedLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/history"
                element={
                    <ProtectedRoute>
                        <AuthenticatedLayout><History /></AuthenticatedLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/search"
                element={
                    <ProtectedRoute>
                        <AuthenticatedLayout><Search /></AuthenticatedLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/profile"
                element={
                    <ProtectedRoute>
                        <AuthenticatedLayout><Profile /></AuthenticatedLayout>
                    </ProtectedRoute>
                }
            />

            {/* Catch-all */}
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    )
}

// ── App root ────────────────────────────────────────────────────────────────
export default function App() {
    return (
        <BrowserRouter>
            <AuthProvider>
                <Toaster
                    position="top-center"
                    toastOptions={{
                        duration: 3500,
                        style: {
                            borderRadius: '12px',
                            background: '#1e293b',
                            color: '#f8fafc',
                            fontSize: '14px',
                        },
                    }}
                />
                <AppRoutes />
            </AuthProvider>
        </BrowserRouter>
    )
}
