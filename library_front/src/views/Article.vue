<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import api from "@/api/axios";

const route = useRoute();
const book = ref(null);
const isLoading = ref(false);
const errorMessage = ref("");

async function fetchBookDetail() {
  isLoading.value = true;
  errorMessage.value = "";

  try {
    const bookId = route.params.id;
    const response = await api.get(`/articles/books/${bookId}/`);
    book.value = response.data;
  } catch (error) {
    book.value = null;
    errorMessage.value = "도서 상세 정보를 불러오지 못했습니다.";
  } finally {
    isLoading.value = false;
  }
}

onMounted(fetchBookDetail);
</script>

<template>
  <main style="max-width: 900px; margin: 0 auto; padding: 24px 16px">
    <p v-if="errorMessage" style="color: #ff6b6b">{{ errorMessage }}</p>
    <p v-if="isLoading">로딩 중...</p>

    <div v-if="book">
      <h1 style="margin: 0; font-weight: 900">{{ book.title }}</h1>
      <p style="opacity: 0.7; margin-top: 8px">{{ book.author }}</p>

      <div v-if="book.cover" style="margin-top: 16px">
        <img
          :src="book.cover"
          alt="cover"
          style="width: 100%; border-radius: 16px"
        />
      </div>

      <pre
        style="
          margin-top: 16px;
          background: #fafafa;
          padding: 12px;
          border-radius: 12px;
          overflow: auto;
        "
        >{{ book }}
      </pre>
    </div>
  </main>
</template>
