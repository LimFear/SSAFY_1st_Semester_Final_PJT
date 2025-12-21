// 1. axios instance
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_ROOT_URL,
  withCredentials: true,
})
export default api

// 2. Request interceptor
import { useAuthStore } from '@/stores/authStore'

api.interceptors.request.use(
  (config) => {
    const store = useAuthStore()

    if (store.accessToken) {
      config.headers.Authorization =
        `Bearer ${store.accessToken}`
    }
    return config
  }
)

// 3. Response interceptor
import { useRouter } from 'vue-router'
const router = useRouter();

api.interceptors.response.use((response) => response, async (error)=>{
    const originalRequest = error.config;
    const status = error.response?.status;
    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refresh = localStorage.getItem('refresh');

      if (refresh) {
        const response = await api.post('/accounts/token/refresh/', {
          refresh
        })
        store.accessToken = response.data.access;
        api.defaults.headers.common.Authorization = `Bearer ${response.data.access}`;
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
        return api(originalRequest);
      }
    }

    if (status === 403) {
      router.push({name: 'home'});
    }
    return Promise.reject(error);
  }
)