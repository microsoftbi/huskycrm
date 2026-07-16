export interface Territory {
  id: number
  name: string
  code?: string
  territory_type: string
  parent_id?: number | null
  description?: string
  is_active: boolean
  owner_id?: number | null
  created_at: string
  updated_at: string
  children: Territory[]
  member_count: number
  account_count: number
  product_count: number
}

export interface TerritoryCreate {
  name: string
  code?: string
  territory_type?: string
  parent_id?: number | null
  description?: string
  is_active?: boolean
  owner_id?: number | null
}

export interface TerritoryUpdate extends Partial<TerritoryCreate> {}

export interface TerritoryTreeNode {
  id: number
  name: string
  code?: string
  territory_type: string
  parent_id?: number | null
  children: TerritoryTreeNode[]
}

export interface TerritoryMember {
  id: number
  territory_id: number
  user_id: number
  role: string
  username?: string
  display_name?: string
  assigned_at: string
}

export interface TerritoryAccount {
  id: number
  territory_id: number
  account_id: number
  account_name?: string
  assigned_at: string
}

export interface TerritoryProduct {
  id: number
  territory_id: number
  product_id: number
  price?: number | null
  is_active: boolean
  product_name?: string
  product_code?: string
  default_price?: number | null
}
