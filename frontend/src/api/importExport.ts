import apiClient from './client'
import type { ImportPreview, ImportConfirmRequest, ImportResult, ImportJob } from '../types/importJob'

export const importExportApi = {
  upload(file: File, objectType: string) {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post<ImportPreview>('/import/upload', formData, {
      params: { object_type: objectType },
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  confirm(data: ImportConfirmRequest) {
    return apiClient.post<ImportResult>('/import/confirm', data)
  },
  listJobs(page = 1) {
    return apiClient.get<{ total: number; page: number; page_size: number; items: ImportJob[] }>(
      '/import/jobs', { params: { page } }
    )
  },
  exportCsv(objectType: string, search = '') {
    return apiClient.get(`/import/export/${objectType}`, {
      params: { q: search },
      responseType: 'blob',
    })
  },
}