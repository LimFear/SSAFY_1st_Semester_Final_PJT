import { ref, computed, watch } from 'vue'
import { defineStore } from 'pinia'
import api from '@/api/axios';

export const useAuthStore = defineStore('counter', () => {

  const accessToken = ref(null);
  const refreshToken = ref(null);
  const username = ref(null);

  const signup = async function(obj){
    try{
      const response = await api.post('/accounts/signup/', {
        username: obj.email,
        password1: obj.pw,
        password2: obj.check,
      });
    } catch(error){
      console.log(error);
      window.alert(error);
    }
  }

  const signout = async function(){
    await api.delete('/accounts/signout/');
  }

  const login = async function(obj){
    try{
      const response = await api.post('/accounts/token/', {
        username: obj.email,
        password: obj.pw,
      });

      accessToken.value = response.data.access;
      refreshToken.value = response.data.refresh;
      username.value = obj.id;

      localStorage.setItem('refresh', refreshToken.value);
      api.defaults.headers.common.Authorization = `Bearer ${accessToken.value}`

    } catch(error){
      console.log(error);
      window.alert(error);
    }
  }

  const logout = async function(){
    // Token Logout
    // try{
    //   const response = await axios.post(`${BASE_URL}/accounts/logout/`);
    //   token.value = null;
    //   username.value = null;
    // } catch(error){
    //   console.log(error);
    //   window.alert(error);
    // }

    accessToken.value = null;
    refreshToken.value = null;
    username.value = null;

    localStorage.removeItem('refresh');
    delete api.defaults.headers.common.Authorization;
  }
  
  return { accessToken, refreshToken, username, signup, signout, login, logout }
}, {persist: true})