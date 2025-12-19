<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBooksStore } from '@/stores/booksStore'
import { useFavoritesStore } from '@/stores/favoritesStore'
import { useAuthStore } from '@/stores/authStore'
import Comments from '@/views/comments.vue'

const route = useRoute()
const router = useRouter()

const booksStore = useBooksStore()
const favoritesStore = useFavoritesStore()
const authStore = useAuthStore()

const bookId = computed(() => String(route.params.id))

async function load() {
  // 추천 표시하려면 전체 목록도 있어야 해서 보장
  if (booksStore.books.length === 0) {
    await booksStore.fetchBooks()
  }
  await booksStore.fetchBook(bookId.value)
}

onMounted(load)
watch(bookId, load)

const recommendedBooks = computed(() => {
  const book = booksStore.selectedBook
  if (!book) return []
  if (!Array.isArray(book.recommends)) return []

  const idSet = new Set(book.recommends.map((value) => String(value)))
  return booksStore.books.filter((b) => idSet.has(String(b.id)))
})

function toggleFavorite() {
  if (!authStore.isLoggedIn) {
    router.push('/login')
    return
  }
  favoritesStore.toggle(bookId.value)
}

function goDetail(nextId) {
  router.push({ name: 'article', params: { id: nextId } })
}
</script>

<template>
  <section>
    <p v-if="booksStore.isLoading">불러오는 중...</p>
    <p v-if="booksStore.error" class="error">{{ booksStore.error }}</p>

    <div v-if="booksStore.selectedBook" class="detail">
      <div class="top">
        <img v-if="booksStore.selectedBook.cover" class="img" :src="booksStore.selectedBook.cover" alt="cover" />
        <div class="meta">
          <h2 class="title">{{ booksStore.selectedBook.title }}</h2>
          <p class="author">{{ booksStore.selectedBook.author }}</p>
          <p class="sub">ISBN: {{ booksStore.selectedBook.isbn }}</p>
          <p class="sub">출판사: {{ booksStore.selectedBook.publisher }}</p>
          <p class="sub">출간일: {{ booksStore.selectedBook.pubDate }}</p>

          <button class="btn" @click="toggleFavorite()">
            {{ favoritesStore.isFavorite(bookId) ? '즐겨찾기 해제' : '즐겨찾기 추가' }}
          </button>
        </div>
      </div>

      <hr class="hr" />

      <h3>설명</h3>
      <p class="desc">{{ booksStore.selectedBook.description }}</p>

      <hr class="hr" />

      <h3>추천 도서</h3>
      <div class="reco">
        <button
          v-for="book in recommendedBooks"
          :key="book.id"
          class="recoItem"
          @click="goDetail(book.id)"
        >
          <img v-if="book.cover" :src="book.cover" alt="cover" />
          <div class="recoText">
            <b>{{ book.title }}</b>
            <div style="opacity:.8">{{ book.author }}</div>
          </div>
        </button>

        <p v-if="recommendedBooks.length === 0" style="opacity:.7;">추천 도서가 없습니다.</p>
      </div>

      <hr class="hr" />

      <!-- 아래에 댓글 출력 -->
      <Comments :book-id="bookId" />
    </div>
  </section>
</template>

<style scoped>
.detail { border:1px solid #2a2a2a; border-radius:14px; padding:14px; background:#141414; }
.top { display:flex; gap:14px; align-items:flex-start; }
.img { width:180px; height:240px; object-fit:cover; border-radius:12px; border:1px solid #2a2a2a; }
.meta { flex:1; }
.title { margin:0; font-weight:900; }
.author { opacity:.85; margin:6px 0 0 0; }
.sub { opacity:.75; margin:6px 0 0 0; font-size:13px; }
.btn { margin-top:12px; border:1px solid #2a2a2a; background:transparent; color:inherit; padding:8px 12px; border-radius:10px; cursor:pointer; }
.hr { border:0; border-top:1px solid #2a2a2a; margin:14px 0; }
.desc { white-space:pre-wrap; line-height:1.6; opacity:.9; }
.reco { display:flex; gap:10px; flex-wrap:wrap; }
.recoItem { width:220px; text-align:left; border:1px solid #2a2a2a; background:#101010; color:inherit; border-radius:12px; overflow:hidden; cursor:pointer; padding:0; }
.recoItem img { width:100%; height:120px; object-fit:cover; display:block; border-bottom:1px solid #2a2a2a; }
.recoText { padding:10px; }
.error { color:#ff6b6b; }
</style>
