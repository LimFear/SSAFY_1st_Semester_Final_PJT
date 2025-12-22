import { ref } from 'vue';
import { defineStore } from 'pinia';
import { jwtDecode } from 'jwt-decode';
import { useAuthStore } from './authStore';
import api from '@/api/axios';

export const useFavoritesStore2 = defineStore('favorites2', () => {
  const favoriteList = ref([]);
  const authStore = useAuthStore();

  const getFavorite = async function () {
    try {
      const response = await api.get(`articles/favorites/`);
      favoriteList.value = response.data;
    } catch (error) {
      console.error("조회 오류:", error);
    }
  };

  const toggle = async function (book_pk) {
    const index = favoriteList.value.findIndex(book => book.id === book_pk);
    const isFavorite = index !== -1;
    if (isFavorite) {
      favoriteList.value.splice(index, 1);
    } else {
      favoriteList.value.push({ id: book_pk });
    }

    try {
      await api.post('articles/favorites/', { book_pk });
      await getFavorite();
    } catch (error) {
      await getFavorite();
      console.log("Error toggling favorite:", error);
    }
  };

  const isFavorite = (bookId) => {
    return favoriteList.value.some(book => book.id === Number(bookId));
  };

  return { toggle, getFavorite, favoriteList, isFavorite };
});