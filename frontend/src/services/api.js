import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// ── Axios instance ──────────────────────────────────────────────────────────
const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

// ── Request interceptor: inject JWT ─────────────────────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── Response interceptor: handle 401 ────────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    const message =
      error.response?.data?.detail || error.message || 'Something went wrong.'
    return Promise.reject(new Error(message))
  },
)

// ── Auth API ────────────────────────────────────────────────────────────────
export const authAPI = {
  register: async (name, email, password) => {
    const { data } = await api.post('/auth/register', { name, email, password })
    return data // { access_token, token_type, user }
  },

  login: async (email, password) => {
    const { data } = await api.post('/auth/login', { email, password })
    return data // { access_token, token_type, user }
  },

  getMe: async () => {
    const { data } = await api.get('/auth/me')
    return data // { id, name, email, preferences, created_at }
  },

  updateProfile: async (payload) => {
    const { data } = await api.put('/auth/profile', payload)
    return data // { id, name, email, preferences }
  },
}

// ── Content API ─────────────────────────────────────────────────────────────
export const contentAPI = {
  generate: async (topic, difficultyLevel, explanationStyle, options = {}) => {
    const { data } = await api.post('/content/generate', {
      topic,
      difficulty_level: difficultyLevel,
      explanation_style: explanationStyle,
      generate_images: options.generateImages ?? true,
      generate_audio: options.generateAudio ?? true,
      generate_video: options.generateVideo ?? false,
    })
    return data
  },

  getHistory: async () => {
    const { data } = await api.get('/content/history')
    return data // { history: [...] }
  },

  getModule: async (moduleId) => {
    const { data } = await api.get(`/content/${moduleId}`)
    return data
  },
}

// ── Search API ──────────────────────────────────────────────────────────────
export const searchAPI = {
  search: async (query) => {
    const { data } = await api.get('/search/', { params: { q: query } })
    return data // { results: [...] }
  },
}

// ── Notes API ───────────────────────────────────────────────────────────────
export const notesAPI = {
  getNotes: async (moduleId, format = 'structured') => {
    const { data } = await api.get(`/notes/${moduleId}`, { params: { format } })
    return data
  },

  downloadPDF: async (moduleId, format = 'structured') => {
    const response = await api.get(`/notes/${moduleId}/pdf`, {
      params: { format },
      responseType: 'blob',
    })
    // Trigger browser download
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `EduGen_${format}_notes.pdf`
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  },
}

export default api
