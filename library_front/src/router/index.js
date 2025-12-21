import { createRouter, createWebHistory } from 'vue-router'

import Main from '@/views/Main.vue'
import BookList from '@/views/BookList.vue'
import Article from '@/views/Article.vue'
import Login from '@/views/Login.vue'
import Signup from '@/views/Signup.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'main', component: Main },
    { path: '/list', name: 'list', component: BookList },
    { path: '/article/:id', name: 'article', component: Article, props: true },
    { path: '/login', name: 'login', component: Login },
    { path: '/signup', name: 'signup', component: Signup },
  ],
})

export default router
