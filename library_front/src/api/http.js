import axios from 'axios'

export const http = axios.create({
  baseURL: '/api/v1',
})

export function setAuthToken(token) {
  if (token) {
    http.defaults.headers.common.Authorization = `Token ${token}`
    return
  }
  delete http.defaults.headers.common.Authorization
}
