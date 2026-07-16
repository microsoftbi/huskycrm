import apiClient from './client'
import type { Product, ProductCreate, ProductUpdate, PaginatedResponse } from '../types/crm'

export const productsApi = {
  list(params: { page?: number; page_size?: number; search?: string } = {}) {
    return apiClient.get<PaginatedResponse<Product>>('/products', { params })
  },
  get(id: number) {
    return apiClient.get<Product>(`/products/${id}`)
  },
  create(data: ProductCreate) {
    return apiClient.post<Product>('/products', data)
  },
  update(id: number, data: ProductUpdate) {
    return apiClient.put<Product>(`/products/${id}`, data)
  },
  delete(id: number) {
    return apiClient.delete(`/products/${id}`)
  },
}
