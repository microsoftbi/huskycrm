import apiClient from './client'
import type { Event, EventCreate, EventUpdate, PaginatedResponse, Task, TaskCreate, TaskUpdate } from '../types/event'

export const eventsApi = {
  // ── Event CRUD ──
  list(params: {
    page?: number
    page_size?: number
    search?: string
    status_filter?: string
    type_filter?: string
    what_id?: string
    what_type?: string
    who_id?: string
  } = {}) {
    return apiClient.get<PaginatedResponse<Event>>('/events', { params })
  },
  get(id: string) {
    return apiClient.get<Event>(`/events/${id}`)
  },
  create(data: EventCreate) {
    return apiClient.post<Event>('/events', data)
  },
  update(id: string, data: EventUpdate) {
    return apiClient.put<Event>(`/events/${id}`, data)
  },
  delete(id: string) {
    return apiClient.delete(`/events/${id}`)
  },

  // ── Check-in / Check-out ──
  checkIn(id: string, location?: string) {
    return apiClient.post<Event>(`/events/${id}/check-in`, null, { params: { location } })
  },
  checkOut(id: string, data: { description?: string; outcome?: string; next_steps?: string } = {}) {
    return apiClient.post<Event>(`/events/${id}/check-out`, null, { params: data })
  },

  // ── Task CRUD ──
  listTasks(eventId: string) {
    return apiClient.get<Task[]>(`/events/${eventId}/tasks`)
  },
  createTask(eventId: string, data: TaskCreate) {
    return apiClient.post<Task>(`/events/${eventId}/tasks`, data)
  },
  updateTask(eventId: string, taskId: string, data: TaskUpdate) {
    return apiClient.put<Task>(`/events/${eventId}/tasks/${taskId}`, data)
  },
  deleteTask(eventId: string, taskId: string) {
    return apiClient.delete(`/events/${eventId}/tasks/${taskId}`)
  },

  // ── Related object event history ──
  listByAccount(accountId: string) {
    return apiClient.get<Event[]>(`/events/by-account/${accountId}`)
  },
  listByContact(contactId: string) {
    return apiClient.get<Event[]>(`/events/by-contact/${contactId}`)
  },
  listByOpportunity(opportunityId: string) {
    return apiClient.get<Event[]>(`/events/by-opportunity/${opportunityId}`)
  },
}
