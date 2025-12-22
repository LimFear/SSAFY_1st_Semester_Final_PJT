<script setup>
import { useAuthStore } from "@/stores/authStore";
import { onMounted, computed } from "vue";
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const router = useRouter();

const userlogout = async function () {
  authStore.logout();
  await router.push("/");
  console.log("logout OK!");
};

const usersignout = async function () {
  await authStore.signout();
  await router.push("/");
  console.log("signout OK!");
};
</script>

<template>
  <header class="navbar">
    <RouterLink class="brand" to="/">Library</RouterLink>

    <nav class="menu">
      <RouterLink class="link" to="/">Main</RouterLink>
      <RouterLink class="link" to="/list">List</RouterLink>
      <RouterLink v-if="!authStore.isLogined" class="link" to="/login"
        >Login</RouterLink
      >
      <RouterLink v-if="!authStore.isLogined" class="link" to="/signup"
        >Signup</RouterLink
      >
      <RouterLink v-if="authStore.isLogined" class="link" to="/favorite"
        >Favorite</RouterLink
      >

      <button
        v-if="authStore.isLogined"
        class="navLinkBtn"
        type="button"
        @click="userlogout()"
      >
        Logout
      </button>
      <button
        v-if="authStore.isLogined"
        class="navLinkBtn"
        type="button"
        @click="usersignout()"
      >
        Signout
      </button>
    </nav>
  </header>

  <main class="page">
    <RouterView />
  </main>
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 10;
  height: 56px;

  display: flex;
  align-items: center;
  justify-content: space-between;

  padding: 0 16px;
  background: #101010;
  border-bottom: 1px solid #2a2a2a;
}

.brand {
  font-weight: 900;
  text-decoration: none;
  color: inherit;
}

.menu {
  display: flex;
  align-items: center;
  gap: 14px;
}

.link {
  text-decoration: none;
  color: inherit;
  opacity: 0.85;
  font-size: 14px;
}

.link.router-link-active {
  opacity: 1;
  font-weight: 800;
}

.btn {
  border: 1px solid #2a2a2a;
  background: transparent;
  color: inherit;
  padding: 6px 10px;
  border-radius: 10px;
  cursor: pointer;
}

.page {
  padding: 16px;
}

.navLinkBtn {
  background: transparent;
  border: 0;
  padding: 0;
  margin: 0;

  color: #fff;
  font: inherit;
  font-size: 14px;

  opacity: 0.85;
  cursor: pointer;
}

.navLinkBtn:hover {
  opacity: 1;
}
</style>
