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
  get(id: number) {
    return apiClient.get<Territory>(`/territories/${id}`)
  },
  create(data: TerritoryCreate) {
    return apiClient.post<Territory>('/territories', data)
  },
  update(id: number, data: TerritoryUpdate) {
    return apiClient.put<Territory>(`/territories/${id}`, data)
  },
  delete(id: number) {
    return apiClient.delete(`/territories/${id}`)
  },

  // ── Tree ──
  getTree() {
    return apiClient.get<TerritoryTreeNode[]>('/territories/tree')
  },

  // ── Members ──
  listMembers(territoryId: number) {
    return apiClient.get<TerritoryMember[]>(`/territories/${territoryId}/members`)
  },
  addMember(territoryId: number, data: { user_id: number; role?: string }) {
    return apiClient.post<TerritoryMember>(`/territories/${territoryId}/members`, data)
  },
  removeMember(territoryId: number, memberId: number) {
    return apiClient.delete(`/territories/${territoryId}/members/${memberId}`)
  },

  // ── Accounts ──
  listAccounts(territoryId: number) {
    return apiClient.get<TerritoryAccount[]>(`/territories/${territoryId}/accounts`)
  },
  addAccount(territoryId: number, data: { account_id: number }) {
    return apiClient.post<TerritoryAccount>(`/territories/${territoryId}/accounts`, data)
  },
  removeAccount(territoryId: number, accountId: number) {
    return apiClient.delete(`/territories/${territoryId}/accounts/${accountId}`)
  },

  // ── Products ──
  listProducts(territoryId: number) {
    return apiClient.get<TerritoryProduct[]>(`/territories/${territoryId}/products`)
  },
  addProduct(territoryId: number, data: { product_id: number; price?: number | null }) {
    return apiClient.post<TerritoryProduct>(`/territories/${territoryId}/products`, data)
  },
  updateProduct(territoryId: number, productId: number, data: { price?: number | null; is_active?: boolean }) {
    return apiClient.put<TerritoryProduct>(`/territories/${territoryId}/products/${productId}`, data)
  },
  removeProduct(territoryId: number, productId: number) {
    return apiClient.delete(`/territories/${territoryId}/products/${productId}`)
  },

  // ── Pipeline ──
  getPipeline(territoryId: number) {
    return apiClient.get<PipelineData>(`/territories/${territoryId}/pipeline`)
  },
}
