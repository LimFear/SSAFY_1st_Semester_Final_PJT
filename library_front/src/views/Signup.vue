<script setup>
import { ref, watch } from 'vue';
import { useAuthStore } from '@/stores/authStore';
import { useRouter } from 'vue-router';

const store = useAuthStore();
const router = useRouter();

const email = ref("");
const pw = ref("");
const check = ref("");

async function signupUser(){
    const obj = {
        email: email.value,
        pw: pw.value,
        check: check.value 
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

                <button class="btn btn-primary w-100" type="submit">가입</button>
                </form>
            </div>
            </div>
        </div>

</template>

<style scoped>

</style>