<script setup>
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/authStore";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const email = ref("");
const pw = ref("");
const errorMessage = ref("");

async function submit() {
  errorMessage.value = "";

  const obj = {
    email: email.value,
    pw: pw.value,
  };

  await authStore.login(obj);

  // 로그인 실패면 여기서 끝
  if (!authStore.isLogined) {
    errorMessage.value = "로그인에 실패했습니다.";
    return;
  }

  // 댓글 쓰려다 넘어온 경우: redirect로 복귀
  const redirect = route.query.redirect;
  if (typeof redirect === "string" && redirect.length > 0) {
    router.replace(redirect);
    return;
  }

  router.replace("/");
}
</script>

<template>
  <section class="wrap">
    <h1>Login</h1>

    <form class="form" @submit.prevent="submit">
      <input v-model="email" class="input" placeholder="email" />
      <input
        v-model="pw"
        type="password"
        class="input"
        placeholder="password"
      />
      <button class="btn" type="submit">로그인</button>
    </form>

    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </section>
</template>

<style scoped>
.wrap {
  max-width: 420px;
  background: #fff;
  color: #000;
  border: 1px solid #e0e0e0;
  padding: 16px;
  border-radius: 12px;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
}
.input {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid #2a2a2a;
  background: #fff;
  color: #000;
}
.btn {
  border: 1px solid #2a2a2a;
  background: #fff;
  color: #000;
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
}
.error {
  color: #ff6b6b;
  margin-top: 10px;
}
</style>
