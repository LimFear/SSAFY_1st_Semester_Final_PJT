import { defineStore } from 'pinia'
import { http } from '@/api/http'

export const useCommentsStore = defineStore('comments', {
  state: () => ({
    items: [],
    isLoading: false,
    error: '',
  }),

  actions: {
    async fetchByBook(bookId) {
      this.isLoading = true
      this.error = ''
      try {
        const response = await http.get(`/books/${bookId}/comments/`)
        this.items = Array.isArray(response.data) ? response.data : (response.data?.results ?? [])
      } catch (error) {
        this.error = '댓글을 불러오지 못했습니다.'
        this.items = []
      } finally {
        this.isLoading = false
      }
    },
  },
})
