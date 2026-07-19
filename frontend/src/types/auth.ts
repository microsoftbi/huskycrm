export interface User {
  id: string
  username: string
  email: string
  display_name: string | null
  is_active: boolean
  is_superuser: boolean
  profile_id: string | null
  profile_name: string | null
  profile_type: string | null
  created_at?: string | null
  updated_at?: string | null
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  display_name?: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface RefreshRequest {
  refresh_token: string
}