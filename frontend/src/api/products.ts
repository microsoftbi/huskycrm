import apiClient from './client'
import type { Product, ProductCreate, ProductUpdate, PaginatedResponse } from '../types/crm'

export const productsApi = {
  list(params: { page?: number; page_size?: number; search?: string } = {}) {
    return apiClient.get<PaginatedResponse<Product>>('/products', { params })
  },
  get(id: string) {
    return apiClient.get<Product>(`/products/${id}`)
  },
  create(data: ProductCreate) {
    return apiClient.post<Product>('/products', data)
  },
  update(id: string, data: ProductUpdate) {
    return apiClient.put<Product>(`/products/${id}`, data)
  },
  delete(id: string) {
    return apiClient.delete(`/products/${id}`)
  },
}
