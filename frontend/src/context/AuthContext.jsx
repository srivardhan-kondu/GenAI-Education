import React, { createContext, useCallback, useContext, useEffect, useReducer } from 'react'
import { authAPI } from '../services/api'

// ── State shape ─────────────────────────────────────────────────────────────
const initialState = {
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    token: localStorage.getItem('token') || null,
    loading: true,  // true until initial /auth/me check finishes
}

// ── Reducer ─────────────────────────────────────────────────────────────────
function authReducer(state, action) {
    switch (action.type) {
        case 'AUTH_SUCCESS':
            return { ...state, user: action.user, token: action.token, loading: false }
        case 'USER_LOADED':
            return { ...state, user: action.user, loading: false }
        case 'AUTH_FAIL':
        case 'LOGOUT':
            return { ...state, user: null, token: null, loading: false }
        default:
            return state
    }
}

// ── Context ─────────────────────────────────────────────────────────────────
const AuthContext = createContext(null)

export function AuthProvider({ children }) {
    const [state, dispatch] = useReducer(authReducer, initialState)

    // ── Persist to localStorage ────────────────────────────────────────────
    useEffect(() => {
        if (state.token) {
            localStorage.setItem('token', state.token)
        } else {
            localStorage.removeItem('token')
        }
        if (state.user) {
            localStorage.setItem('user', JSON.stringify(state.user))
        } else {
            localStorage.removeItem('user')
        }
    }, [state.token, state.user])

    // ── Load user on mount (if token exists) ───────────────────────────────
    useEffect(() => {
        if (!state.token) {
            dispatch({ type: 'AUTH_FAIL' })
            return
        }
        authAPI
            .getMe()
            .then((user) => dispatch({ type: 'USER_LOADED', user }))
            .catch(() => dispatch({ type: 'AUTH_FAIL' }))
    }, []) // eslint-disable-line react-hooks/exhaustive-deps

    // ── Actions ────────────────────────────────────────────────────────────
    const login = useCallback(async (email, password) => {
        const data = await authAPI.login(email, password)
        dispatch({ type: 'AUTH_SUCCESS', user: data.user, token: data.access_token })
    }, [])

    const register = useCallback(async (name, email, password) => {
        const data = await authAPI.register(name, email, password)
        dispatch({ type: 'AUTH_SUCCESS', user: data.user, token: data.access_token })
    }, [])

    const logout = useCallback(() => {
        dispatch({ type: 'LOGOUT' })
    }, [])

    const updateUser = useCallback((user) => {
        dispatch({ type: 'USER_LOADED', user })
    }, [])

    return (
        <AuthContext.Provider value={{ ...state, login, register, logout, updateUser }}>
            {children}
        </AuthContext.Provider>
    )
}

// ── Custom hook ─────────────────────────────────────────────────────────────
export function useAuth() {
    const ctx = useContext(AuthContext)
    if (!ctx) throw new Error('useAuth must be used within <AuthProvider>')
    return ctx
}
