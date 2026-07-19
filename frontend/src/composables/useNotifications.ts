import { ref, onMounted, onUnmounted } from 'vue'
import { notificationsApi } from '../api/notifications'
import type { Notification } from '../types/notification'

export function useNotifications() {
  const unreadCount = ref(0)
  const recentNotifications = ref<Notification[]>([])
  let pollTimer: number | null = null

  async function fetchUnreadCount() {
    try {
      const { data } = await notificationsApi.unreadCount()
      unreadCount.value = data.count
    } catch {
      // silent
    }
  }

  async function fetchRecent() {
    try {
      const { data } = await notificationsApi.list(1, 10)
      recentNotifications.value = data.items
    } catch {
      // silent
    }
  }

  async function markAsRead(id: string) {
    try {
      await notificationsApi.markRead(id)
      await fetchUnreadCount()
      await fetchRecent()
    } catch {
      // silent
    }
  }

  async function markAllRead() {
    try {
      await notificationsApi.markAllRead()
      unreadCount.value = 0
      recentNotifications.value = recentNotifications.value.map(n => ({ ...n, is_read: true }))
    } catch {
      // silent
    }
  }

  function startPolling() {
    fetchUnreadCount()
    pollTimer = window.setInterval(fetchUnreadCount, 30000)
  }

  function stopPolling() {
    if (pollTimer !== null) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  onMounted(startPolling)
  onUnmounted(stopPolling)

  return {
    unreadCount,
    recentNotifications,
    fetchUnreadCount,
    fetchRecent,
    markAsRead,
    markAllRead,
  }
}