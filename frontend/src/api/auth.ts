import apiClient from './client'
import type { LoginRequest, RegisterRequest, TokenResponse, User } from '../types/auth'

export const authApi = {
  login(data: LoginRequest) {
    return apiClient.post<TokenResponse>('/auth/login', data)
  },
  register(data: RegisterRequest) {
    return apiClient.post<User>('/auth/register', data)
  },
  refresh(refreshToken: string) {
    return apiClient.post<TokenResponse>('/auth/refresh', { refresh_token: refreshToken })
  },
  me() {
    return apiClient.get<User>('/auth/me')
  },
  listUsers() {
    return apiClient.get<User[]>('/auth/users')
  },
  updateUser(userId: string, data: { display_name?: string; email?: string; is_active?: boolean }) {
    return apiClient.put<User>(`/auth/users/${userId}`, data)
  },
}
