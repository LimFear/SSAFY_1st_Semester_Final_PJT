import { defineStore } from "pinia";
import api from "@/api/axios";
import { useAuthStore } from "@/stores/authStore";

export const useCommentsStore = defineStore("comments", {
  state: () => ({
    items: [],
    isLoading: false,
    error: "",
  }),

  actions: {
    async fetchByBook(bookId) {
      this.isLoading = true;
      this.error = "";

      try {
        const response = await api.get(`/articles/books/${bookId}/comments/`);
        const data = response.data;

        if (Array.isArray(data)) {
          this.items = data;
        } else {
          this.items = data?.results ?? [];
        }
      } catch (error) {
        this.items = [];
        this.error = "댓글을 불러오지 못했습니다.";
      } finally {
        this.isLoading = false;
      }
    },

    async createComment(bookId, content) {
      const authStore = useAuthStore();

      if (!authStore.isLogined) {
        const error = new Error("LOGIN_REQUIRED");
        error.code = "LOGIN_REQUIRED";
        throw error;
      }

      const headers = {
        Authorization: `Bearer ${authStore.accessToken}`,
      };

      const response = await api.post(
        `/articles/books/${bookId}/comments/`,
        { content },
        { headers }
      );

      // 작성 즉시 화면 반영
      this.items.unshift(response.data);
      return response.data;
    },

    async deleteComment(commentId) {
      const authStore = useAuthStore();

      const headers = {
        Authorization: `Bearer ${authStore.accessToken}`,
      };

      await api.delete(`/articles/comments/${commentId}/`, { headers });
      this.items = this.items.filter((comment) => comment.id !== commentId);
    },
  },
});
