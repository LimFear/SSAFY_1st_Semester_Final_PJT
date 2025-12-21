import axios from 'axios'
import router from '@/router'

// Instance..........
const api = axios.create({
  baseURL: '/api/v1',
  withCredentials: true,
})

// Request..........
api.interceptors.request.use(async (config) => {
  const { useAuthStore } = await import('@/stores/authStore')
  const store = useAuthStore()

  if (store.accessToken) {
    config.headers.Authorization = `Bearer ${store.accessToken}`
  }
  return config
})

// Response..........
api.interceptors.response.use(
  response => response,
  async (error) => {
    const { useAuthStore } = await import('@/stores/authStore')
    const store = useAuthStore()
    const originalRequest = error.config
    
    if (!originalRequest) return Promise.reject(error)

    if (originalRequest.url.includes('accounts/logout/') || 
        originalRequest.url.includes('accounts/token/refresh/')) {
      return Promise.reject(error)
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const response = await api.post('accounts/token/refresh/')
        store.accessToken = response.data.access
        return api(originalRequest)
      } catch (refreshError) {
        store.accessToken = null
        store.isLogined = false
        router.push('/login')
        return Promise.reject(refreshError)
      }
    }
    return Promise.reject(error)
  }
)

export default api