import { defineStore } from 'pinia'
import api from '@/api/axios'
import { normalizeBook, normalizeBookList } from '@/utils/adapters'

export const useBooksStore = defineStore('books', {
  state: () => ({
    books: [],
    selectedBook: null,
    isLoading: false,
    error: '',
  }),

  actions: {
    async fetchBooks() {
      this.isLoading = true
      this.error = ''
      try {
        const response = await api.get('/articles/books/')
        this.books = normalizeBookList(response.data)
      } catch (error) {
        this.error = '도서 목록을 불러오지 못했습니다.'
        this.books = []
      } finally {
        this.isLoading = false
      }
    },

    async fetchBook(bookId) {
      this.isLoading = true
      this.error = ''
      try {
        const response = await api.get(`/articles/books/${bookId}/`)
        const raw = Array.isArray(response.data) ? response.data[0] : response.data
        this.selectedBook = normalizeBook(raw)
      } catch (error) {
        this.error = '도서 상세를 불러오지 못했습니다.'
        this.selectedBook = null
      } finally {
        this.isLoading = false
      }
    },
  },
})
