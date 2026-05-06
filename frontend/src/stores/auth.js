import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/composables/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('vantage_token'))
  const user  = ref(null)

  async function login(username, password) {
    const res = await api.post('/auth/login/', { username, password })
    token.value = res.data.token
    localStorage.setItem('vantage_token', token.value)
  }

  function logout() {
    token.value = null
    user.value  = null
    localStorage.removeItem('vantage_token')
  }

  return { token, user, login, logout }
})
