export interface Territory {
  id: string
  name: string
  code?: string
  territory_type: string
  parent_id?: string | null
  description?: string
  is_active: boolean
  owner_id?: string | null
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
  parent_id?: string | null
  description?: string
  is_active?: boolean
  owner_id?: string | null
}

export interface TerritoryUpdate extends Partial<TerritoryCreate> {}

export interface TerritoryTreeNode {
  id: string
  name: string
  code?: string
  territory_type: string
  parent_id?: string | null
  children: TerritoryTreeNode[]
}

export interface TerritoryMember {
  id: string
  territory_id: string
  user_id: string
  role: string
  username?: string
  display_name?: string
  assigned_at: string
}

export interface TerritoryAccount {
  id: string
  territory_id: string
  account_id: string
  account_name?: string
  assigned_at: string
}

export interface TerritoryProduct {
  id: string
  territory_id: string
  product_id: string
  price?: number | null
  is_active: boolean
  product_name?: string
  product_code?: string
  default_price?: number | null
}
