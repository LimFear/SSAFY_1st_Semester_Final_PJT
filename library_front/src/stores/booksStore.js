import { defineStore } from 'pinia'
import { http } from '@/api/http'
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
        const response = await http.get('/books/')
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
        const response = await http.get(`/books/${bookId}`)
        // 응답이 객체/배열 둘 다 가능하게 처리
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
