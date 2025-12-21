<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const pw = ref('')

async function submit() {
    const obj = {
        email: email.value,
        pw: pw.value
    }
    await authStore.login(obj);
    router.push('/');
}
</script>

<template>
  <section class="wrap">
    <h1>Login</h1>

    <form class="form" @submit.prevent="submit">
      <input v-model="email" class="input" placeholder="email" />
      <input v-model="pw" type="password" class="input" placeholder="password" />
      <button class="btn" type="submit">로그인</button>
    </form>

    <p v-if="authStore.loginError" class="error">{{ authStore.loginError }}</p>
  </section>
</template>

<style scoped>
.wrap { max-width: 420px; }
.form { display:flex; flex-direction:column; gap:10px; margin-top:10px; }
.input { padding:10px 12px; border-radius:10px; border:1px solid #2a2a2a; background:transparent; color:inherit; }
.btn { border:1px solid #2a2a2a; background:transparent; color:inherit; padding:10px 12px; border-radius:10px; cursor:pointer; }
.error { color:#ff6b6b; margin-top:10px; }
</style>
