<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "@/api/axios";
import { useAuthStore } from "@/stores/authStore";

const props = defineProps({
  bookId: { type: [String, Number], required: true },
});

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const comments = ref([]);
const isLoading = ref(false);
const errorMessage = ref("");

const newComment = ref("");
const createLoading = ref(false);
const createError = ref("");

function parseJwtPayload(token) {
  try {
    if (!token) return null;
    const parts = token.split(".");
    if (parts.length !== 3) return null;

    const base64Url = parts[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const json = decodeURIComponent(
      atob(base64)
        .split("")
        .map((char) => `%${`00${char.charCodeAt(0).toString(16)}`.slice(-2)}`)
        .join("")
    );
    return JSON.parse(json);
  } catch {
    return null;
  }
}

const myUserId = computed(() => {
  const payload = parseJwtPayload(authStore.accessToken);
  if (!payload) return null;
  // simplejwt 기본: user_id
  return payload.user_id ?? payload.userId ?? null;
});

function goLogin() {
  router.push({ path: "/login", query: { redirect: route.fullPath } });
}

async function fetchComments() {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    const response = await api.get(`/articles/books/${props.bookId}/comments/`);
    const data = response.data;
    comments.value = Array.isArray(data) ? data : data?.results ?? [];
  } catch (error) {
    // 혹시 백엔드가 "댓글 0개면 404"로 되어 있어도 UX는 빈 리스트가 맞음
    if (error?.response?.status === 404) {
      comments.value = [];
      errorMessage.value = "";
    } else {
      comments.value = [];
      errorMessage.value = "댓글을 불러오지 못했습니다.";
    }
  } finally {
    isLoading.value = false;
  }
}

async function submitComment() {
  const content = newComment.value.trim();
  createError.value = "";

  if (content.length === 0) return;

  if (!authStore.isLogined) {
    goLogin();
    return;
  }

  createLoading.value = true;
  try {
    const headers = { Authorization: `Bearer ${authStore.accessToken}` };
    const response = await api.post(
      `/articles/books/${props.bookId}/comments/`,
      { content },
      { headers }
    );
    comments.value.unshift(response.data);
    newComment.value = "";
  } catch (error) {
    if (error?.response?.status === 401) {
      goLogin();
      return;
    }
    createError.value = "댓글 작성에 실패했습니다.";
  } finally {
    createLoading.value = false;
  }
}

function isMine(comment) {
  if (!authStore.isLogined) return false;
  if (myUserId.value == null) return false;
  // comment.user 는 FK id(정수)로 내려오는 전제
  return Number(comment.user) === Number(myUserId.value);
}

async function deleteComment(commentId) {
  if (!authStore.isLogined) {
    goLogin();
    return;
  }

  try {
    const headers = { Authorization: `Bearer ${authStore.accessToken}` };
    await api.delete(`/articles/comments/${commentId}/`, { headers });
    comments.value = comments.value.filter((c) => c.id !== commentId);
  } catch (error) {
    if (error?.response?.status === 401) {
      goLogin();
      return;
    }
    alert("댓글 삭제에 실패했습니다.");
  }
}

onMounted(fetchComments);
watch(() => props.bookId, fetchComments);
</script>

<template>
  <section class="comments">
    <h3>댓글 ({{ comments.length }})</h3>

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
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

    <p v-if="isLoading" class="muted">불러오는 중...</p>
    <p v-else-if="comments.length === 0" class="muted">댓글이 없습니다.</p>

    <ul v-else class="commentList">
      <li v-for="c in comments" :key="c.id" class="commentItem">
        <div class="commentTop">
          <div class="commentMeta">
            <span>작성자: {{ c.username ?? c.user }}</span>
            <span v-if="c.created_at"> · {{ c.created_at }}</span>
          </div>

          <!-- ✅ 내 댓글이면 삭제 버튼 표시 -->
          <button
            v-if="isMine(c)"
            class="deleteBtn"
            @click="deleteComment(c.id)"
          >
            삭제
          </button>
        </div>

        <div class="commentContent">{{ c.content }}</div>
      </li>
    </ul>
  </section>
</template>

<style scoped>
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
}
.commentBtn {
  border: 1px solid #2a2a2a;
  background: #fff;
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
.commentTop {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}
.commentMeta {
  font-size: 12px;
  opacity: 0.75;
}
.commentContent {
  margin-top: 6px;
}
.deleteBtn {
  border: 1px solid #d33;
  background: #fff;
  color: #d33;
  padding: 6px 10px;
  border-radius: 8px;
  cursor: pointer;
}
.muted {
  opacity: 0.7;
}
.error {
  color: #ff6b6b;
}
</style>
