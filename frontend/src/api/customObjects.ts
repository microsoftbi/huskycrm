import apiClient from './client'
import type { CustomObjectDef, CustomObjectCreate, CustomFieldCreate, CustomRecord, PaginatedResponse } from '../types/crm'

export const customObjectsApi = {
  // Object definitions
  listObjects() {
    return apiClient.get<CustomObjectDef[]>('/custom-objects')
  },
  getObject(id: string) {
    return apiClient.get<CustomObjectDef>(`/custom-objects/${id}`)
  },
  createObject(data: CustomObjectCreate) {
    return apiClient.post<CustomObjectDef>('/custom-objects', data)
  },
  deleteObject(id: string) {
    return apiClient.delete(`/custom-objects/${id}`)
  },

  // Fields
  addField(objId: string, data: CustomFieldCreate) {
    return apiClient.post(`/custom-objects/${objId}/fields`, data)
  },
  deleteField(objId: string, fieldId: string) {
    return apiClient.delete(`/custom-objects/${objId}/fields/${fieldId}`)
  },

  // Records (by object ID)
  listRecords(objId: string, params: { page?: number; page_size?: number } = {}) {
    return apiClient.get<PaginatedResponse<CustomRecord>>(`/custom-objects/${objId}/records`, { params })
  },
  getRecord(objId: string, recordId: string) {
    return apiClient.get<CustomRecord>(`/custom-objects/${objId}/records/${recordId}`)
  },
  createRecord(objId: string, fields: Record<string, any>) {
    return apiClient.post<CustomRecord>(`/custom-objects/${objId}/records`, { fields })
  },
  updateRecord(objId: string, recordId: string, fields: Record<string, any>) {
    return apiClient.put<CustomRecord>(`/custom-objects/${objId}/records/${recordId}`, { fields })
  },
  deleteRecord(objId: string, recordId: string) {
    return apiClient.delete(`/custom-objects/${objId}/records/${recordId}`)
  },

  // Universal API (by object API name)
  listRecordsByName(apiName: string, params: { page?: number; page_size?: number } = {}) {
    return apiClient.get<PaginatedResponse<CustomRecord>>(`/custom-objects/by-name/${apiName}/records`, { params })
  },
  createRecordByName(apiName: string, fields: Record<string, any>) {
    return apiClient.post<CustomRecord>(`/custom-objects/by-name/${apiName}/records`, { fields })
  },
}