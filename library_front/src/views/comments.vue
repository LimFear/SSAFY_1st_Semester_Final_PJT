<script setup>
import { computed, onMounted, watch } from 'vue'
import { useCommentsStore } from '@/stores/commentsStore'

const props = defineProps({
  bookId: { type: [String, Number], required: true },
})

const commentsStore = useCommentsStore()
const bookIdText = computed(() => String(props.bookId))

async function load() {
  await commentsStore.fetchByBook(bookIdText.value)
}

onMounted(load)
watch(bookIdText, load)
</script>

<template>
  <section>
    <h3>댓글</h3>

    <p v-if="commentsStore.isLoading">불러오는 중...</p>
    <p v-if="commentsStore.error" class="error">{{ commentsStore.error }}</p>

    <ul v-if="commentsStore.items.length">
      <li v-for="comment in commentsStore.items" :key="comment.id">
        <b>{{ comment.author ?? '익명' }}</b> : {{ comment.content ?? comment.text ?? '' }}
      </li>
    </ul>

    <p v-else style="opacity:.7;">댓글이 없습니다.</p>
  </section>
</template>

<style scoped>
.error { color:#ff6b6b; }
ul { padding-left:18px; }
</style>
