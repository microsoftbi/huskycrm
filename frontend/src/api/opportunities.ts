import apiClient from './client'
import type { Opportunity, OpportunityCreate, OpportunityUpdate, PaginatedResponse, PipelineData, Stage, LineItem, LineItemCreate } from '../types/crm'

export const opportunitiesApi = {
  list(params: { page?: number; page_size?: number; search?: string; stage_id?: string; account_id?: string } = {}) {
    return apiClient.get<PaginatedResponse<Opportunity>>('/opportunities', { params })
  },
  get(id: string) {
    return apiClient.get<Opportunity>(`/opportunities/${id}`)
  },
  create(data: OpportunityCreate) {
    return apiClient.post<Opportunity>('/opportunities', data)
  },
  update(id: string, data: OpportunityUpdate) {
    return apiClient.put<Opportunity>(`/opportunities/${id}`, data)
  },
  delete(id: string) {
    return apiClient.delete(`/opportunities/${id}`)
  },
  getStages() {
    return apiClient.get<Stage[]>('/opportunities/stages')
  },
  getPipeline() {
    return apiClient.get<PipelineData>('/opportunities/pipeline')
  },
  // ── Line items ──
  listLineItems(opportunityId: string) {
    return apiClient.get<LineItem[]>(`/opportunities/${opportunityId}/line-items`)
  },
  addLineItem(opportunityId: string, data: LineItemCreate) {
    return apiClient.post<LineItem>(`/opportunities/${opportunityId}/line-items`, data)
  },
  removeLineItem(opportunityId: string, itemId: string) {
    return apiClient.delete(`/opportunities/${opportunityId}/line-items/${itemId}`)
  },
  listEvents(opportunityId: string) {
    return apiClient.get<import('../types/event').Event[]>(`/events/by-opportunity/${opportunityId}`)
  },
}
