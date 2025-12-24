<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { Lock, Eye, EyeOff, User, Check } from 'lucide-vue-next';
import { useAuthStore } from '@/stores/authStore';
import { useRouter } from 'vue-router';
import api from '@/api/axios';

const store = useAuthStore();
const router = useRouter();
const emit = defineEmits(['switchToLogin']);

// 폼 상태
const username = ref('');
const password1 = ref('');
const password2 = ref('');
const showPassword1 = ref(false);
const showPassword2 = ref(false);

// 카테고리 데이터
interface Category { id: number; name: string; }
const categoryList = ref<Category[]>([]);
const selectedCategories = ref<number[]>([]);

onMounted(async () => {
  try {
    const response = await api.get('articles/categories/');
    categoryList.value = response.data;
  } catch (error) {
    console.error("카테고리 로드 실패", error);
  }
});

// 카테고리 선택/해제 토글 함수
const toggleCategory = (id: number) => {
  const index = selectedCategories.value.indexOf(id);
  if (index > -1) {
    selectedCategories.value.splice(index, 1); // 이미 있으면 제거
  } else {
    selectedCategories.value.push(id); // 없으면 추가
  }
};

const switchToLogin = function(){
  router.push({name: 'login'});
}

// 배경용 리스트 (무한 흐름을 위해 복제)
const row1 = computed(() => [...categoryList.value].sort((a, b) => a.id - b.id));
const row2 = computed(() => [...categoryList.value].sort((a, b) => b.id - a.id));

const handleSubmit = async () => {
  if (password1.value !== password2.value) {
    alert('비밀번호가 일치하지 않습니다.');
    return;
  }
  try {
    await store.signup({
      email: username.value,
      pw: password1.value,
      check: password2.value,
      categories: selectedCategories.value
    });
    await store.login({ email: username.value, pw: password1.value });
    router.push('/');
  } catch (error) {
    alert('가입 실패');
  }
};
</script>

<template>
  <div class="relative min-h-screen w-full bg-gray-50 flex items-center justify-center overflow-hidden font-sans">
    
    <div class="absolute inset-0 z-0 flex flex-col justify-center gap-10 opacity-40">
      <div class="flex gap-6 animate-marquee-left whitespace-nowrap">
        <button 
          v-for="(cat, idx) in [...row1, ...row1, ...row1]" :key="`row1-${cat.id}-${idx}`"
          @click="toggleCategory(cat.id)"
          :class="[
            'px-8 py-4 rounded-full border-2 transition-all duration-300 text-xl font-bold flex items-center gap-2 shadow-sm',
            selectedCategories.includes(cat.id) 
              ? 'bg-black border-black text-white scale-110 z-10' 
              : 'bg-white border-gray-200 text-gray-400 hover:border-black hover:text-black'
          ]"
        >
          {{ cat.name }}
          <Check v-if="selectedCategories.includes(cat.id)" :size="20" />
        </button>
      </div>

      <div class="flex gap-6 animate-marquee-right whitespace-nowrap">
        <button 
          v-for="(cat, idx) in [...row2, ...row2, ...row2]" :key="`row2-${cat.id}-${idx}`"
          @click="toggleCategory(cat.id)"
          :class="[
            'px-8 py-4 rounded-full border-2 transition-all duration-300 text-xl font-bold flex items-center gap-2 shadow-sm',
            selectedCategories.includes(cat.id) 
              ? 'bg-black border-black text-white scale-110 z-10' 
              : 'bg-white border-gray-200 text-gray-400 hover:border-black hover:text-black'
          ]"
        >
          {{ cat.name }}
          <Check v-if="selectedCategories.includes(cat.id)" :size="20" />
        </button>
      </div>
    </div>

    <div class="relative z-10 w-full max-w-md px-4">
      <div class="bg-white/80 backdrop-blur-xl rounded-[2.5rem] shadow-[0_32px_64px_-12px_rgba(0,0,0,0.15)] p-10 border border-white/40">
        <div class="mb-10 text-center">
          <h1 class="text-4xl font-black text-black tracking-tighter mb-3">Create Account</h1>
          <p class="text-gray-500 font-medium">떠다니는 키워드를 클릭해 선택하세요</p>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div class="group">
            <input v-model="username" type="text" placeholder="아이디 (이메일)" class="auth-input" required />
          </div>
          
          <div class="relative group">
            <input :type="showPassword1 ? 'text' : 'password'" v-model="password1" placeholder="비밀번호" class="auth-input" required />
            <button type="button" @click="showPassword1 = !showPassword1" class="absolute right-5 top-1/2 -translate-y-1/2 text-gray-400">
              <EyeOff v-if="showPassword1" :size="20" /><Eye v-else :size="20" />
            </button>
          </div>

          <div class="relative group">
            <input :type="showPassword2 ? 'text' : 'password'" v-model="password2" placeholder="비밀번호 확인" class="auth-input" required />
            <button type="button" @click="showPassword2 = !showPassword2" class="absolute right-5 top-1/2 -translate-y-1/2 text-gray-400">
              <EyeOff v-if="showPassword2" :size="20" /><Eye v-else :size="20" />
            </button>
          </div>

          <div class="pt-2 flex items-center justify-between text-sm font-bold">
            <span class="text-black">Selected Tags</span>
            <span class="text-white bg-black px-3 py-1 rounded-full">{{ selectedCategories.length }}</span>
          </div>

          <button type="submit" class="w-full bg-black text-white py-5 rounded-2xl font-black text-xl hover:bg-gray-800 transition-all active:scale-95 shadow-2xl mt-4">
            Get Started
          </button>
        </form>

        <p class="mt-8 text-center text-gray-500 font-medium">
          이미 계정이 있나요? <button @click="switchToLogin" class="text-black font-extrabold hover:underline transition-all">로그인하기</button>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "../tailwind.css";

.auth-input {
  @apply w-full px-6 py-4 bg-gray-100/50 border-2 border-transparent rounded-2xl focus:outline-none focus:border-black focus:bg-white transition-all text-lg font-medium placeholder:text-gray-400;
}

/* 무한 애니메이션 */
@keyframes marquee-left {
  0% { transform: translateX(0); }
  100% { transform: translateX(-33.33%); }
}

@keyframes marquee-right {
  0% { transform: translateX(-33.33%); }
  100% { transform: translateX(0); }
}

.animate-marquee-left {
  animation: marquee-left 40s linear infinite;
}

.animate-marquee-right {
  animation: marquee-right 45s linear infinite;
}

/* 마우스를 올렸을 때 배경 흐름 멈춤 (선택하기 쉽게) */
.animate-marquee-left:hover,
.animate-marquee-right:hover {
  animation-play-state: paused;
}
</style>