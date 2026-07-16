import { onMounted } from 'vue'
import { useAuthStore } from '../stores/authStore'

export function useAuth() {
  const auth = useAuthStore()

  onMounted(() => {
    if (!auth.user && localStorage.getItem('access_token')) {
      auth.fetchUser()
    }
  })

  return auth
}
