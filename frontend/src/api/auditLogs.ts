import apiClient from './client'
import type { TimelineEntry } from '../types/auditLog'

export const auditLogsApi = {
  getTimeline(objectType: string, objectId: string, page = 1) {
    return apiClient.get<TimelineEntry[]>(`/timeline/${objectType}/${objectId}`, { params: { page } })
  },
}