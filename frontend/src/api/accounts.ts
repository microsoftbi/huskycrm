import apiClient from './client'
import type { Account, AccountCreate, AccountUpdate, PaginatedResponse } from '../types/crm'

export const accountsApi = {
  list(params: { page?: number; page_size?: number; search?: string } = {}) {
    return apiClient.get<PaginatedResponse<Account>>('/accounts', { params })
  },
  get(id: number) {
    return apiClient.get<Account>(`/accounts/${id}`)
  },
  create(data: AccountCreate) {
    return apiClient.post<Account>('/accounts', data)
  },
  update(id: number, data: AccountUpdate) {
    return apiClient.put<Account>(`/accounts/${id}`, data)
  },
  delete(id: number) {
    return apiClient.delete(`/accounts/${id}`)
  },
}
