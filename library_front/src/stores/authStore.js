import { ref, computed, watch } from 'vue'
import { defineStore } from 'pinia'
import api from '@/api/axios';

export const useAuthStore = defineStore('auth', () => {

  const accessToken = ref(null);

  const isLogined = ref(false);

  const signup = async function(obj){
    try{
      const response = await api.post('accounts/signup/', {
        username: obj.email,
        password1: obj.pw,
        password2: obj.check,
      })

    } catch(error){
      console.log(error);
      window.alert(error);
    }
  }


  const signout = async function(){
    await api.delete('accounts/signout/');
    accessToken.value = null;
    isLogined.value = false;
  }

  const login = async function(obj){
    try{
      const response = await api.post('accounts/token/', {
        username: obj.email,
        password: obj.pw,
      });
      accessToken.value = response.data.access;
      console.log(accessToken.value);
      isLogined.value = true;
      
    } catch(error){
      console.log(error);
      window.alert(error);
      isLogined.value = false;
    }
  }

  const logout = async function() {
    try {
      await api.post('accounts/logout/');
    } catch (error) {
      console.log('Server logout failed or session expired');
    } finally {
      accessToken.value = null;
      isLogined.value = false;
      router.push('/');
    }
  }

  const refresh = async function () {
    try {
      const response = await api.post('accounts/token/refresh/');
      accessToken.value = response.data.access;
      isLogined.value = true;
      console.log("Token Refreshed!")
    } catch {
      accessToken.value = null;
      isLogined.value = false;
    }
  }
  
  return { accessToken, isLogined, signup, signout, login, logout, refresh }
}, {persist: true})