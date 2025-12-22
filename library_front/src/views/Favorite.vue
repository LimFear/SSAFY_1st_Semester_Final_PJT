<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useBooksStore } from '@/stores/booksStore'
import { useFavoritesStore } from '@/stores/favoritesStore'
import { useAuthStore } from '@/stores/authStore'
import { useFavoritesStore2 } from '@/stores/favoriteStorev2'

const router = useRouter()
const booksStore = useBooksStore()
const favoritesStore = useFavoritesStore()
const authStore = useAuthStore()
const favoriteStore2 = useFavoritesStore2()

const query = ref('')

onMounted(async () => {
  await favoriteStore2.getFavorite()
})

const filteredBooks = computed(() => {
  const q = query.value.trim().toLowerCase()
  
  // 즐겨찾기 목록에 포함된 책만 필터링하려면
  const isFavorite = (bookId) => {
    return favoriteStore2.favoriteList.some(favorite => favorite.id === bookId);
  }

  // 검색어가 없으면, 즐겨찾기 목록에 포함된 책만 필터링
  if (!q) {
    return booksStore.books.filter(book => isFavorite(book.id));
  }

  // 검색어가 있을 때, 즐겨찾기 목록에 포함되었는지 여부도 함께 체크
  return booksStore.books.filter((book) => {
    const title = String(book.title ?? '').toLowerCase();
    const author = String(book.author ?? '').toLowerCase();
    const isBookFavorite = isFavorite(book.id);

    // 책 제목이나 저자에 검색어가 포함되거나 즐겨찾기 목록에 포함된 책만 반환
    return (title.includes(q) || author.includes(q)) && isBookFavorite;
  });
});


function goDetail(bookId) {
  router.push({ name: 'article', params: { id: bookId } })
}

function toggleFavorite(bookId) {
  console.log(authStore.isLogined);
  if (!authStore.isLogined) {
    router.push('/login')
    return
  }
  else {
    favoriteStore2.toggle(bookId);
  }
  // favoritesStore.toggle(bookId)
}
</script>

<template>
  <section>
    <h2>도서 목록</h2>

    <input v-model="query" class="search" placeholder="제목/저자 검색" />

    <p v-if="booksStore.isLoading">불러오는 중...</p>
    <p v-if="booksStore.error" class="error">{{ booksStore.error }}</p>

    <div class="grid">
      <div v-for="book in filteredBooks" :key="book.id" class="card">
        <div class="cover" @click="goDetail(book.id)">
          <img v-if="book.cover" :src="book.cover" alt="cover" />
        </div>

        <div class="body">
          <div class="title">{{ book.title }}</div>
          <div class="author">{{ book.author }}</div>

          <div class="actions">
            <button class="btn" @click="goDetail(book.id)">더보기</button>
            <button class="btn" @click="toggleFavorite(book.id)">
              {{ favoritesStore.isFavorite(book.id) ? '★' : '☆' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.search { width:100%; max-width:520px; padding:10px 12px; border-radius:10px; border:1px solid #2a2a2a; background:transparent; color:inherit; margin:12px 0; }
.grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:14px; }
.card { border: 1px solid #e5e5e5; border-radius: 14px; overflow: hidden; background: #ffffff; color: #111; }
.cover { height: 160px; background: #f0f0f0; border-bottom: 1px solid #e5e5e5; cursor: pointer; }
.btn { border: 1px solid #e5e5e5; background: #fff; color: #111; padding: 6px 10px; border-radius: 10px; cursor: pointer; }
.cover img { width:100%; height:100%; object-fit:cover; display:block; }
.body { padding:12px; }
.title { font-weight:900; }
.author { opacity:.8; margin-top:4px; }
.actions { display:flex; gap:8px; margin-top:10px; }
.error { color:#ff6b6b; }
</style>
