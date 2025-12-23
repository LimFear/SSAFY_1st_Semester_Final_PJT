<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "@/api/axios";
import { useBooksStore } from "@/stores/booksStore";
import { useAuthStore } from "@/stores/authStore";
import { useFavoritesStore2 } from "@/stores/favoriteStorev2";
import { jwtDecode } from "jwt-decode";

const route = useRoute();
const router = useRouter();

const booksStore = useBooksStore();
const favoritesStore2 = useFavoritesStore2();
const authStore = useAuthStore();

const bookId = computed(() => String(route.params.id));

/* ---------------- 댓글 상태 ---------------- */

const Token = authStore.accessToken;
const decoded = jwtDecode(Token);
const tokenUserId = decoded.user_id;

const comments = ref([]);
const commentsLoading = ref(false);
const commentsError = ref("");

const newComment = ref("");
const createLoading = ref(false);
const createError = ref("");

async function fetchComments() {
  commentsLoading.value = true;
  commentsError.value = "";
  try {
    const response = await api.get(`/articles/books/${bookId.value}/comments/`);
    const data = response.data;
    comments.value = Array.isArray(data) ? data : data?.results ?? [];
  } catch (error) {
    // 백엔드가 "댓글 0개면 404"로 되어 있는 경우를 대비해서 404는 빈 배열로 처리
    if (error?.response?.status === 404) {
      comments.value = [];
      commentsError.value = "";
    } else {
      comments.value = [];
      commentsError.value = "댓글을 불러오지 못했습니다.";
    }
  } finally {
    commentsLoading.value = false;
  }
}

async function submitComment() {
  const content = newComment.value.trim();
  createError.value = "";

  if (content.length === 0) return;

  // 비로그인 -> 로그인으로 이동 + 돌아오기
  if (!authStore.isLogined) {
    router.push({ name: "Login", query: { redirect: route.fullPath } });
    return;
  }

  createLoading.value = true;
  try {
    const headers = {
      Authorization: `Bearer ${authStore.accessToken}`,
    };

    const response = await api.post(
      `/articles/books/${bookId.value}/comments/`,
      { content },
      { headers }
    );

    // 작성 즉시 화면 반영
    comments.value.unshift(response.data);
    newComment.value = "";
  } catch (error) {
    // 토큰 만료/비로그인 처리 -> 로그인으로
    if (error?.response?.status === 401) {
      router.push({ name: "Login", query: { redirect: route.fullPath } });
      return;
    }
    createError.value = "댓글 작성에 실패했습니다.";
  } finally {
    createLoading.value = false;
  }
}

const deleteComment = async function (obj) {
  const commentPK = obj.comment_pk;

  try {
    const headers = {
      Authorization: `Bearer ${authStore.accessToken}`,
    };
    const response = await api.delete(`/articles/comments/${commentPK}/`, {
      headers,
    });

    const updatedCommentsResponse = await api.get(
      `/articles/books/${bookId.value}/comments/`
    );
    console.log(updatedCommentsResponse);
    comments.value = updatedCommentsResponse.data;
    newComment.value = "";
  } catch (error) {
    // 토큰 만료/비로그인 처리 -> 로그인으로
    if (error?.response?.status === 401) {
      router.push({ name: "Login", query: { redirect: route.fullPath } });
      return;
    }
    createError.value = "댓글 삭제에 실패했습니다.";
  } finally {
    createLoading.value = false;
  }
};

/* ---------------- 책 로드 ---------------- */
async function load() {
  if (booksStore.books.length === 0) {
    await booksStore.fetchBooks();
  }
  await booksStore.fetchBook(bookId.value);
  await fetchComments();
}

onMounted(load);
watch(bookId, load);

const recommendedBooks = computed(() => {
  const book = booksStore.selectedBook;
  if (!book) return [];
  if (!Array.isArray(book.recommends)) return [];

  const idSet = new Set(book.recommends.map((value) => String(value)));
  return booksStore.books.filter((b) => idSet.has(String(b.id)));
});

function toggleFavorite(bookId) {
  // ✅ authStore는 isLogined 입니다
  if (!authStore.isLogined) {
    router.push({ name: "Login", query: { redirect: route.fullPath } });
    return;
  }
  favoritesStore2.toggle(bookId);
}

function goDetail(nextId) {
  router.push({ name: "article", params: { id: nextId } });
}
</script>

<template>
  <section>
    <p v-if="booksStore.isLoading">불러오는 중...</p>
    <p v-if="booksStore.error" class="error">{{ booksStore.error }}</p>

    <div v-if="booksStore.selectedBook" class="detail">
      <div class="top">
        <img
          v-if="booksStore.selectedBook.cover"
          class="img"
          :src="booksStore.selectedBook.cover"
          alt="cover"
        />
        <div class="meta">
          <h2 class="title">{{ booksStore.selectedBook.title }}</h2>
          <p class="author">{{ booksStore.selectedBook.author }}</p>
          <p class="sub">ISBN: {{ booksStore.selectedBook.isbn }}</p>
          <p class="sub">출판사: {{ booksStore.selectedBook.publisher }}</p>
          <p class="sub">출간일: {{ booksStore.selectedBook.pubDate }}</p>

          <button class="btn" @click="toggleFavorite(bookId)">
            {{ favoritesStore2.isFavorite(bookId) ? "즐겨찾기 해제" : "즐겨찾기 추가" }}
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
            <div class="recoAuthor">{{ book.author }}</div>
          </div>
        </button>

        <p v-if="recommendedBooks.length === 0" class="muted">
          추천 도서가 없습니다.
        </p>
      </div>

      <hr class="hr" />

      <!-- ✅ 댓글 섹션 -->
      <section class="comments">
        <!-- <h1>{{ comments }}</h1> -->
        <h3>댓글 ({{ comments.length }})</h3>

        <p v-if="commentsError" class="error">{{ commentsError }}</p>

        <div class="commentForm">
          <input
            v-model="newComment"
            class="commentInput"
            placeholder="댓글을 입력하세요"
            :disabled="createLoading"
            @keydown.enter="submitComment"
          />
          <button
            class="commentBtn"
            :disabled="createLoading"
            @click="submitComment"
          >
            {{ createLoading ? "작성중" : "작성" }}
          </button>
        </div>

        <p v-if="createError" class="error">{{ createError }}</p>

        <p v-if="commentsLoading" class="muted">불러오는 중...</p>
        <p v-else-if="comments.length === 0" class="muted">댓글이 없습니다.</p>

        <ul v-else class="commentList">
          <li v-for="c in comments" :key="c.id" class="commentItem">
            <div class="commentMeta">
              <span class="commentUser"
                >작성자: {{ c.username ?? c.user }}</span
              >
              <span class="commentDate" v-if="c.created_at">
                · {{ c.created_at }}</span
              >
            </div>
            <div class="commentContent">{{ c.content }}</div>
            <!-- =------------------------------------------------------ -->
            <button
              v-if="c.user == tokenUserId"
              v-on:click="
                deleteComment({ user_pk: tokenUserId, comment_pk: c.id })
              "
            >
              삭제
            </button>
          </li>
        </ul>
      </section>
    </div>
  </section>
</template>

<style scoped>
.detail {
  border: 1px solid #2a2a2a;
  border-radius: 14px;
  padding: 14px;
  background: #ffffff;
  color: #000;
}
.top {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}
.img {
  width: 180px;
  height: 240px;
  object-fit: cover;
  border-radius: 12px;
  border: 1px solid #2a2a2a;
}
.meta {
  flex: 1;
}
.title {
  margin: 0;
  font-weight: 900;
}
.author {
  opacity: 0.85;
  margin: 6px 0 0 0;
}
.sub {
  opacity: 0.75;
  margin: 6px 0 0 0;
  font-size: 13px;
}
.btn {
  margin-top: 12px;
  border: 1px solid #2a2a2a;
  background: #fff;
  color: #000;
  padding: 8px 12px;
  border-radius: 10px;
  cursor: pointer;
}
.hr {
  border: 0;
  border-top: 1px solid #2a2a2a;
  margin: 14px 0;
}
.desc {
  white-space: pre-wrap;
  line-height: 1.6;
  opacity: 0.9;
}

.reco {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.recoItem {
  width: 220px;
  text-align: left;
  border: 1px solid #2a2a2a;
  background: #ffffff; /* ✅ 검은 배경 -> 흰 배경 */
  color: #000; /* ✅ 글자색 검정 */
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  padding: 0;
}
.recoItem img {
  width: 100%;
  height: 120px;
  object-fit: cover;
  display: block;
  border-bottom: 1px solid #2a2a2a;
}
.recoText {
  padding: 10px;
}
.recoAuthor {
  opacity: 0.8;
}

.comments {
  margin-top: 12px;
}
.commentForm {
  display: flex;
  gap: 8px;
  margin: 10px 0;
}
.commentInput {
  flex: 1;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid #2a2a2a;
  background: #fff;
  color: #000;
}
.commentBtn {
  border: 1px solid #2a2a2a;
  background: #fff;
  color: #000;
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
}
.commentList {
  list-style: none;
  padding: 0;
  margin: 10px 0 0 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.commentItem {
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  padding: 10px;
  background: #fff;
}
.commentMeta {
  font-size: 12px;
  opacity: 0.75;
}
.commentContent {
  margin-top: 6px;
}

.muted {
  opacity: 0.7;
}
.error {
  color: #ff6b6b;
}
</style>
