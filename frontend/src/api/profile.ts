import apiClient from './client'
import type { User } from '../types/auth'

export interface ProfileUpdateData {
  display_name?: string
  email?: string
}

export interface PasswordChangeData {
  current_password: string
  new_password: string
  confirm_password: string
}

export interface UserTerritory {
  territory_id: string
  territory_name: string
  territory_code: string | null
  territory_type: string
  role: string
  manager_name: string | null
  manager_username: string | null
}

export const profileApi = {
  updateProfile(data: ProfileUpdateData) {
    return apiClient.put<User>('/auth/profile', data)
  },
  changePassword(data: PasswordChangeData) {
    return apiClient.put<{ message: string }>('/auth/password', data)
  },
  getMyTerritories() {
    return apiClient.get<UserTerritory[]>('/auth/my-territories')
  },
}
