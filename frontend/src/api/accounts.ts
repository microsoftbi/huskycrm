import apiClient from './client'
import type { Account, AccountCreate, AccountUpdate, PaginatedResponse } from '../types/crm'

export const accountsApi = {
  list(params: { page?: number; page_size?: number; search?: string } = {}) {
    return apiClient.get<PaginatedResponse<Account>>('/accounts', { params })
  },
  get(id: string) {
    return apiClient.get<Account>(`/accounts/${id}`)
  },
  create(data: AccountCreate) {
    return apiClient.post<Account>('/accounts', data)
  },
  update(id: string, data: AccountUpdate) {
    return apiClient.put<Account>(`/accounts/${id}`, data)
  },
  delete(id: string) {
    return apiClient.delete(`/accounts/${id}`)
  },
  listTerritories(accountId: string) {
    return apiClient.get<any[]>(`/accounts/${accountId}/territories`)
  },
  listEvents(accountId: string) {
    return apiClient.get<import('../types/event').Event[]>(`/events/by-account/${accountId}`)
  },
}
