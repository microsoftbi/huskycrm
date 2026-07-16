import apiClient from './client'
import type { Opportunity, OpportunityCreate, OpportunityUpdate, PaginatedResponse, PipelineData, Stage, LineItem, LineItemCreate } from '../types/crm'

export const opportunitiesApi = {
  list(params: { page?: number; page_size?: number; search?: string; stage_id?: number } = {}) {
    return apiClient.get<PaginatedResponse<Opportunity>>('/opportunities', { params })
  },
  get(id: number) {
    return apiClient.get<Opportunity>(`/opportunities/${id}`)
  },
  create(data: OpportunityCreate) {
    return apiClient.post<Opportunity>('/opportunities', data)
  },
  update(id: number, data: OpportunityUpdate) {
    return apiClient.put<Opportunity>(`/opportunities/${id}`, data)
  },
  delete(id: number) {
    return apiClient.delete(`/opportunities/${id}`)
  },
  getStages() {
    return apiClient.get<Stage[]>('/opportunities/stages')
  },
  getPipeline() {
    return apiClient.get<PipelineData>('/opportunities/pipeline')
  },
  // ── Line items ──
  listLineItems(opportunityId: number) {
    return apiClient.get<LineItem[]>(`/opportunities/${opportunityId}/line-items`)
  },
  addLineItem(opportunityId: number, data: LineItemCreate) {
    return apiClient.post<LineItem>(`/opportunities/${opportunityId}/line-items`, data)
  },
  removeLineItem(opportunityId: number, itemId: number) {
    return apiClient.delete(`/opportunities/${opportunityId}/line-items/${itemId}`)
  },
}
