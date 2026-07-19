import apiClient from './client'
import type { Notification, NotificationListResponse, UnreadCountResponse } from '../types/notification'

export const notificationsApi = {
  list(page = 1, pageSize = 20) {
    return apiClient.get<NotificationListResponse>('/notifications', { params: { page, page_size: pageSize } })
  },
  unreadCount() {
    return apiClient.get<UnreadCountResponse>('/notifications/unread-count')
  },
  markRead(id: string) {
    return apiClient.put<Notification>(`/notifications/${id}/read`)
  },
  markAllRead() {
    return apiClient.put('/notifications/read-all')
  },
}