<script setup lang="ts">
import { ref } from 'vue';
import { Lock, Eye, EyeOff, User } from 'lucide-vue-next';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';

// 부모에게 화면 전환을 요청하는 이벤트 정의

const store = useAuthStore();

const username = ref('');
const password = ref('');
const showPassword = ref(false);

const router = useRouter();

const handleSubmit = async function () {

  const obj = {
    email: username.value,
    pw: password.value
  }

  await store.login(obj);
  if (store.isLogined){
    router.push({name: 'main'});
  }
};

const switchToSignup = function() {
  router.push({name: 'signup'});
}
</script>

<template>
<div class="min-h-screen bg-gray-100 flex items-center justify-center p-3">
  <div class="w-full max-w-md">
    <div class="bg-white rounded-2xl shadow-2xl p-8 border border-gray-100">
      <div class="mb-8">
        <h1 class="text-black text-2xl font-bold mb-2">로그인</h1>
        <p class="text-gray-600">계정에 로그인하세요</p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-6">
        <div>
          <label for="username" class="block text-black mb-2">아이디</label>
          <div class="relative">
            <div class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
              <User :size="20" />
            </div>
            <input
              id="username"
              type="text"
              v-model="username"
              placeholder="아이디를 입력하세요"
              class="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all"
              required
            />
          </div>
        </div>

        <div>
          <label for="password" class="block text-black mb-2">비밀번호</label>
          <div class="relative">
            <div class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
              <Lock :size="20" />
            </div>
            <input
              id="password"
              :type="showPassword ? 'text' : 'password'"
              v-model="password"
              placeholder="비밀번호를 입력하세요"
              class="w-full pl-12 pr-12 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all"
              required
            />
            <button
              type="button"
              @click="showPassword = !showPassword"
              class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <EyeOff v-if="showPassword" :size="20" />
              <Eye v-else :size="20" />
            </button>
          </div>
        </div>

        <button
          type="submit"
          class="w-full bg-black text-white py-3 rounded-lg hover:bg-gray-800 transition-all active:scale-[0.98] font-medium"
        >
          로그인
        </button>
      </form>

      <div class="mt-6 text-center text-sm">
        <p class="text-gray-600">
          아이디가 없으신가요?
          <button
            @click="switchToSignup"
            class="text-black font-semibold hover:underline transition-all ml-1"
          >
            회원가입
          </button>
        </p>
      </div>
    </div>
  </div>
</div>
</template>