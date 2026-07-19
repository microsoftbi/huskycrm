import apiClient from './client'
import type { Profile, ProfileBrief, ProfileCreate, ProfileUpdate } from '../types/profile'

export const profilesApi = {
  list() {
    return apiClient.get<Profile[]>('/profiles')
  },
  brief() {
    return apiClient.get<ProfileBrief[]>('/profiles/brief')
  },
  get(id: string) {
    return apiClient.get<Profile>(`/profiles/${id}`)
  },
  create(data: ProfileCreate) {
    return apiClient.post<Profile>('/profiles', data)
  },
  update(id: string, data: ProfileUpdate) {
    return apiClient.put<Profile>(`/profiles/${id}`, data)
  },
  delete(id: string) {
    return apiClient.delete(`/profiles/${id}`)
  },
}