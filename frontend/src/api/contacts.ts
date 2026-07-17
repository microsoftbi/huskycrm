import apiClient from './client'
import type { Contact, ContactCreate, ContactUpdate, PaginatedResponse, ContactAccount } from '../types/crm'

export const contactsApi = {
  list(params: { page?: number; page_size?: number; search?: string; account_id?: string } = {}) {
    return apiClient.get<PaginatedResponse<Contact>>('/contacts', { params })
  },
  get(id: string) {
    return apiClient.get<Contact>(`/contacts/${id}`)
  },
  create(data: ContactCreate) {
    return apiClient.post<Contact>('/contacts', data)
  },
  update(id: string, data: ContactUpdate) {
    return apiClient.put<Contact>(`/contacts/${id}`, data)
  },
  delete(id: string) {
    return apiClient.delete(`/contacts/${id}`)
  },
  listAccounts(contactId: string) {
    return apiClient.get<ContactAccount[]>(`/contacts/${contactId}/accounts`)
  },
  addAccount(contactId: string, accountId: string) {
    return apiClient.post<ContactAccount>(`/contacts/${contactId}/accounts`, { account_id: accountId })
  },
  removeAccount(contactId: string, accountId: string) {
    return apiClient.delete(`/contacts/${contactId}/accounts/${accountId}`)
  },
  listEvents(contactId: string) {
    return apiClient.get<import('../types/event').Event[]>(`/events/by-contact/${contactId}`)
  },
}
