import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '../types/auth'
import { authApi } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!user.value)

  async function login(username: string, password: string) {
    loading.value = true
    try {
      const { data } = await authApi.login({ username, password })
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      await fetchUser()
      if (!user.value) {
        throw new Error('Failed to fetch user profile')
      }
      return true
    } finally {
      loading.value = false
    }
  }

  async function register(username: string, email: string, password: string, displayName?: string) {
    loading.value = true
    try {
      await authApi.register({ username, email, password, display_name: displayName })
      return await login(username, password)
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    const token = localStorage.getItem('access_token')
    if (!token) {
      user.value = null
      return false
    }
    try {
      const { data } = await authApi.me()
      user.value = data
      return true
    } catch (e) {
      user.value = null
      console.error('fetchUser failed:', e)
      return false
    }
  }

  function logout() {
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return { user, loading, isAuthenticated, login, register, fetchUser, logout }
})
