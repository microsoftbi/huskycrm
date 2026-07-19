export interface Notification {
  id: string
  user_id: string
  title: string
  message: string | null
  notification_type: 'workflow' | 'system'
  reference_type: string | null
  reference_id: string | null
  is_read: boolean
  created_at: string | null
}

export interface NotificationListResponse {
  total: number
  page: number
  page_size: number
  items: Notification[]
}

export interface UnreadCountResponse {
  count: number
}