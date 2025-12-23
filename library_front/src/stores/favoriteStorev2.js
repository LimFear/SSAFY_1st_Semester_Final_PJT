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
    // 1. 타입을 확실하게 Number로 변환 (book_pk가 문자열로 넘어올 때를 대비)
    const targetId = Number(book_pk);
    
    // 2. 현재 상태 확인
    const index = favoriteList.value.findIndex(book => Number(book.id) === targetId);
    const alreadyFavorite = index !== -1;

    // 3. UI 우선 반영 (사용자 경험 향상)
    if (alreadyFavorite) {
      favoriteList.value.splice(index, 1);
    } else {
      favoriteList.value.push({ id: targetId });
    }

    try {
      // 4. 서버에 요청
      await api.post('articles/favorites/', { book_pk: targetId });
      
      // 5. 서버와 데이터 최종 동기화 (서버 응답 후 리스트 갱신)
      await getFavorite();
    } catch (error) {
      console.error("Error toggling favorite:", error);
      // 에러 발생 시 원래 상태로 복구하기 위해 다시 불러옴
      await getFavorite();
      
      // 만약 서버에서 500이 난다면 백엔드 view 로직에서 
      // get_or_create나 filter().delete() 처리가 정확한지 확인이 필요합니다.
    }
  };

  const isFavorite = (bookId) => {
    // 비교 대상을 모두 Number로 강제 변환하여 타입 오류 방지
    return favoriteList.value.some(book => Number(book.id) === Number(bookId));
  };

  return { toggle, getFavorite, favoriteList, isFavorite };
});