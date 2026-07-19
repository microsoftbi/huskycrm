import apiClient from './client'
import type { SearchResults } from '../types/search'

export const searchApi = {
  search(q: string, limit = 5) {
    return apiClient.get<SearchResults>('/search', { params: { q, limit } })
  },
}