import { defineStore } from 'pinia'
import { http, setAuthToken } from '@/api/http'

const TOKEN_KEY = 'library_token_v1'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || '',
    loginError: '',
  }),

  getters: {
    isLoggedIn(state) {
      return Boolean(state.token)
    },
  },

  actions: {
    init() {
      setAuthToken(this.token)
    },

    async login({ email, pw }) {
      this.loginError = ''

      const response = await http.post('/accounts/login', { email, pw })
      const token = response?.data?.token || ''

      if (!token) {
        this.token = ''
        localStorage.removeItem(TOKEN_KEY)
        setAuthToken('')
        this.loginError = '아이디/비밀번호가 올바르지 않습니다.'
        return false
      }

      this.token = token
      localStorage.setItem(TOKEN_KEY, token)
      setAuthToken(token)
      return true
    },

    logout() {
      this.token = ''
      this.loginError = ''
      localStorage.removeItem(TOKEN_KEY)
      setAuthToken('')
    },
  },
})
