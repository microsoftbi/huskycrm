import apiClient from './client'
import type { Contact, ContactCreate, ContactUpdate, PaginatedResponse } from '../types/crm'

export const contactsApi = {
  list(params: { page?: number; page_size?: number; search?: string; account_id?: number } = {}) {
    return apiClient.get<PaginatedResponse<Contact>>('/contacts', { params })
  },
  get(id: number) {
    return apiClient.get<Contact>(`/contacts/${id}`)
  },
  create(data: ContactCreate) {
    return apiClient.post<Contact>('/contacts', data)
  },
  update(id: number, data: ContactUpdate) {
    return apiClient.put<Contact>(`/contacts/${id}`, data)
  },
  delete(id: number) {
    return apiClient.delete(`/contacts/${id}`)
  },
}
