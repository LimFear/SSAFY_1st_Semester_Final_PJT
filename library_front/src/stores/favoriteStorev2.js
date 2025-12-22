import { ref } from 'vue';
import { defineStore } from 'pinia';
import { jwtDecode } from 'jwt-decode';
import { useAuthStore } from './authStore';
import api from '@/api/axios';

export const useFavoritesStore2 = defineStore('favorites2', () => {
  const favoriteList = ref([]);
  const authStore = useAuthStore();

  // 즐겨찾기 목록을 갱신하는 함수
  const getFavorite = async function () {
    const Token = authStore.accessToken;
    const decoded = jwtDecode(Token);
    const tokenUserId = decoded.user_id;

    try {
      const response = await api.get(`articles/favorites/?user_pk=${tokenUserId}`);
      favoriteList.value = response.data;
    } catch (error) {
      console.error("즐겨찾기 목록 조회 오류:", error);
    }
  };

  // 즐겨찾기 추가/제거를 토글하는 함수
  const toggle = async function (book_pk) {
    const Token = authStore.accessToken;
    const decoded = jwtDecode(Token);
    const tokenUserId = decoded.user_id;

    try {
      // 최신 즐겨찾기 목록을 먼저 가져옵니다.
      await getFavorite();

      // 즐겨찾기 목록에 해당 책이 있는지 확인
      const isFavorite = favoriteList.value.some(favorite => favorite.pk === book_pk);
      let response;

      console.log('isFavorite:', isFavorite);

      if (isFavorite) {
        // 이미 즐겨찾기에 있는 경우, 제거
        response = await api.delete('articles/favorites/', { data: { book_pk, user_pk: tokenUserId } });
        console.log('Book removed from favorites:', response);
      } else {
        // 즐겨찾기에 없는 경우, 추가
        response = await api.post('articles/favorites/', { book_pk, user_pk: tokenUserId });
        console.log('Book added to favorites:', response);
      }

      // 동작 후, 즐겨찾기 목록을 다시 가져옵니다. (토글 후 최신 상태 반영)
      await getFavorite();
    } catch (error) {
      console.log("Error toggling favorite:", error);
    }
  };

  return { toggle, getFavorite, favoriteList };
});
