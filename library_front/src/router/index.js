import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useRouter } from 'vue-router'

import Main from '@/views/Main.vue'
import BookList from '@/views/BookList.vue'
import Article from '@/views/Article.vue'
import Login from '@/views/Login.vue'
import Signup from '@/views/Signup.vue'
import favorite from '@/views/Favorite.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'main', component: Main },
    { path: '/list', name: 'list', component: BookList },
    { path: '/article/:id', name: 'article', component: Article, props: true },
    { path: '/login', name: 'login', component: Login },
    { path: '/signup', name: 'signup', component: Signup },
    { path: '/favorite', name: 'favorite', component: favorite}
  ],
})

router.beforeEach((to)=>{
  const store = useAuthStore();
  const route = useRouter();

  if (!store.isLogined && to.name === 'list'){
    window.alert('로그인 하라!');
    route.push({name: 'login'})
  }
})

export default router
