import apiClient from './client'
import type {
  Territory, TerritoryCreate, TerritoryUpdate, TerritoryTreeNode,
  TerritoryMember, TerritoryAccount, TerritoryProduct,
} from '../types/territory'
import type { PipelineData } from '../types/crm'

export const territoriesApi = {
  // ── CRUD ──
  list(params: { search?: string } = {}) {
    return apiClient.get<Territory[]>('/territories', { params })
  },
  get(id: string) {
    return apiClient.get<Territory>(`/territories/${id}`)
  },
  create(data: TerritoryCreate) {
    return apiClient.post<Territory>('/territories', data)
  },
  update(id: string, data: TerritoryUpdate) {
    return apiClient.put<Territory>(`/territories/${id}`, data)
  },
  delete(id: string) {
    return apiClient.delete(`/territories/${id}`)
  },

  // ── Tree ──
  getTree() {
    return apiClient.get<TerritoryTreeNode[]>('/territories/tree')
  },

  // ── Members ──
  listMembers(territoryId: string) {
    return apiClient.get<TerritoryMember[]>(`/territories/${territoryId}/members`)
  },
  addMember(territoryId: string, data: { user_id: string; role?: string }) {
    return apiClient.post<TerritoryMember>(`/territories/${territoryId}/members`, data)
  },
  removeMember(territoryId: string, memberId: string) {
    return apiClient.delete(`/territories/${territoryId}/members/${memberId}`)
  },

  // ── Accounts ──
  listAccounts(territoryId: string) {
    return apiClient.get<TerritoryAccount[]>(`/territories/${territoryId}/accounts`)
  },
  addAccount(territoryId: string, data: { account_id: string }) {
    return apiClient.post<TerritoryAccount>(`/territories/${territoryId}/accounts`, data)
  },
  removeAccount(territoryId: string, accountId: string) {
    return apiClient.delete(`/territories/${territoryId}/accounts/${accountId}`)
  },

  // ── Products ──
  listProducts(territoryId: string) {
    return apiClient.get<TerritoryProduct[]>(`/territories/${territoryId}/products`)
  },
  addProduct(territoryId: string, data: { product_id: string; price?: number | null }) {
    return apiClient.post<TerritoryProduct>(`/territories/${territoryId}/products`, data)
  },
  updateProduct(territoryId: string, productId: string, data: { price?: number | null; is_active?: boolean }) {
    return apiClient.put<TerritoryProduct>(`/territories/${territoryId}/products/${productId}`, data)
  },
  removeProduct(territoryId: string, productId: string) {
    return apiClient.delete(`/territories/${territoryId}/products/${productId}`)
  },

  // ── Pipeline ──
  getPipeline(territoryId: string) {
    return apiClient.get<PipelineData>(`/territories/${territoryId}/pipeline`)
  },
}
