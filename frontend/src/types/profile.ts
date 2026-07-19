export interface Profile {
  id: string
  name: string
  profile_type: string
  description: string | null
  is_system: boolean
  user_count: number
  users: ProfileUser[]
  created_at?: string
  updated_at?: string
}

export interface ProfileUser {
  id: string
  username: string
  display_name: string | null
  email: string
  is_active: boolean
}

export interface ProfileBrief {
  id: string
  name: string
  profile_type: string
  is_system: boolean
}

export interface ProfileCreate {
  name: string
  profile_type: string
  description?: string
}

export interface ProfileUpdate {
  name?: string
  profile_type?: string
  description?: string
}