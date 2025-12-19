import { defineStore } from 'pinia'

const FAVORITES_KEY = 'library_favorites_v1'

export const useFavoritesStore = defineStore('favorites', {
  state: () => ({
    favoriteIds: JSON.parse(localStorage.getItem(FAVORITES_KEY) || '[]'),
  }),

  getters: {
    favoriteIdSet(state) {
      return new Set(state.favoriteIds.map((value) => String(value)))
    },
    isFavorite() {
      return (bookId) => this.favoriteIdSet.has(String(bookId))
    },
  },

  actions: {
    persist() {
      localStorage.setItem(FAVORITES_KEY, JSON.stringify(this.favoriteIds))
    },

    toggle(bookId) {
      const idText = String(bookId)
      const exists = this.favoriteIdSet.has(idText)

      if (exists) {
        this.favoriteIds = this.favoriteIds.filter((value) => String(value) !== idText)
      } else {
        this.favoriteIds = [...this.favoriteIds, bookId]
      }

      this.persist()
    },
  },
})
