<script setup>
import { ref, watch, onMounted } from 'vue';
import { useAuthStore } from '@/stores/authStore';
import { useRouter } from 'vue-router';
import api from '@/api/axios';

const store = useAuthStore();
const router = useRouter();

const email = ref("");
const pw = ref("");
const check = ref("");

const categoryList = ref([]); // 서버에서 받아올 전체 카테고리
const selectedCategories = ref([]); // 사용자가 체크한 카테고리 ID들

onMounted(async () => {
    try {
        const response = await api.get('articles/categories/'); 
        categoryList.value = response.data;
    } catch (error) {
        console.error("카테고리를 불러오는데 실패했습니다.", error);
    }
});

async function signupUser(){
    const obj = {
        email: email.value,
        pw: pw.value,
        check: check.value,
        categories: selectedCategories.value
    }
    try{
        await store.signup(obj);
        await store.login({
            email: email.value, 
            pw: pw.value
        });
        await router.push('/');
    } catch(error){
        window.alert('FAILED!');
    }
}

</script>

<template>
    <h1>SIGNUP PAGE</h1>
        <div class="container d-flex justify-content-center align-items-center vh-100">
            <div class="card shadow" style="width: 400px;">
            <div class="card-body">
                <h3 class="text-center mb-4">Signup</h3>

                <form v-on:submit.prevent="signupUser">
                <div class="mb-3">
                    <label class="form-label">아이디</label>
                    <input
                    type="text"
                    class="form-control"
                    v-model="email"
                    placeholder="아이디를 입력하세요"
                    />
                </div>

                <div class="mb-3">
                    <label class="form-label">비밀번호</label>
                    <input
                    type="password"
                    class="form-control"
                    v-model="pw"
                    placeholder="비밀번호를 입력하세요"
                    />
                </div>

                <div class="mb-3">
                    <label class="form-label">비밀번호 확인</label>
                    <input
                    type="password"
                    class="form-control"
                    v-model="check"
                    placeholder="비밀번호를 확인하세요"
                    />
                </div>

                <div class="mb-4">
                        <label class="form-label">관심 카테고리 (복수 선택 가능)</label>
                        <div class="d-flex flex-wrap gap-2">
                            <div v-for="category in categoryList" :key="category.id" class="form-check">
                                <input 
                                    class="form-check-input" 
                                    type="checkbox" 
                                    :value="category.id" 
                                    v-model="selectedCategories"
                                    :id="'cat-' + category.id"
                                >
                                <label class="form-check-label" :for="'cat-' + category.id">
                                    {{ category.name }}
                                </label>
                        </div>
                    </div>
                </div>

                <button class="btn btn-primary w-100" type="submit">가입</button>
                </form>
            </div>
            </div>
        </div>

</template>

<style scoped>

</style>