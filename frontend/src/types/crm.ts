export interface Account {
  id: number
  name: string
  industry?: string
  phone?: string
  website?: string
  email?: string
  billing_street?: string
  billing_city?: string
  billing_state?: string
  billing_zip?: string
  billing_country?: string
  description?: string
  owner_id?: number
  created_at: string
  updated_at: string
}

export interface AccountCreate {
  name: string
  industry?: string
  phone?: string
  website?: string
  email?: string
  billing_street?: string
  billing_city?: string
  billing_state?: string
  billing_zip?: string
  billing_country?: string
  description?: string
  owner_id?: number
}

export interface AccountUpdate extends Partial<AccountCreate> {}

export interface Contact {
  id: number
  first_name: string
  last_name: string
  email?: string
  phone?: string
  mobile_phone?: string
  title?: string
  department?: string
  account_id?: number
  owner_id?: number
  created_at: string
  updated_at: string
}

export interface ContactCreate {
  first_name: string
  last_name: string
  email?: string
  phone?: string
  mobile_phone?: string
  title?: string
  department?: string
  account_id?: number
  owner_id?: number
}

export interface ContactUpdate extends Partial<ContactCreate> {}

export interface Product {
  id: number
  name: string
  product_code?: string
  description?: string
  price?: number
  cost?: number
  category?: string
  is_active?: boolean
  owner_id?: number
  created_at: string
  updated_at: string
}

export interface ProductCreate {
  name: string
  product_code?: string
  description?: string
  price?: number
  cost?: number
  category?: string
  is_active?: boolean
  owner_id?: number
}

export interface ProductUpdate extends Partial<ProductCreate> {}

export interface Stage {
  id: number
  name: string
  probability: number
  sort_order: number
  is_closed_won: boolean
  is_closed_lost: boolean
}

export interface Opportunity {
  id: number
  name: string
  account_id?: number
  stage_id: number
  amount?: number
  probability?: number
  close_date?: string
  description?: string
  owner_id?: number
  created_at: string
  updated_at: string
}

export interface OpportunityCreate {
  name: string
  account_id?: number
  stage_id: number
  amount?: number
  probability?: number
  close_date?: string
  description?: string
  owner_id?: number
}

export interface OpportunityUpdate extends Partial<OpportunityCreate> {}

export interface PipelineStageData {
  stage: Stage
  opportunities: Opportunity[]
  total_amount: number
  count: number
}

export interface PipelineData {
  stages: PipelineStageData[]
}

export interface PaginatedResponse<T> {
  total: number
  page: number
  page_size: number
  items: T[]
}

export interface LineItem {
  id: number
  opportunity_id: number
  product_id: number
  quantity: number
  unit_price: number
  total_price: number
  created_at: string
}

export interface LineItemCreate {
  product_id: number
  quantity: number
  unit_price: number
}

// ── Custom Objects ────────────────────────────────────────────────

export interface CustomFieldDef {
  id: number
  object_id: number
  api_name: string
  label: string
  field_type: string
  is_required: boolean
  is_unique: boolean
  default_value?: string | null
  max_length?: number | null
  picklist_values?: string[] | null
  precision_total?: number | null
  precision_scale?: number | null
  lookup_object_id?: number | null
  display_order: number
  created_at: string
  updated_at: string
}

export interface CustomObjectDef {
  id: number
  api_name: string
  label: string
  plural_label?: string
  description?: string
  table_name: string
  is_active: boolean
  fields: CustomFieldDef[]
  created_at: string
  updated_at: string
}

export interface CustomFieldCreate {
  api_name: string
  label: string
  field_type: string
  is_required?: boolean
  is_unique?: boolean
  default_value?: string | null
  max_length?: number | null
  picklist_values?: string[] | null
  precision_total?: number | null
  precision_scale?: number | null
  lookup_object_id?: number | null
  display_order?: number
}

export interface CustomObjectCreate {
  api_name: string
  label: string
  plural_label?: string
  description?: string
  fields: CustomFieldCreate[]
}

export interface CustomRecord {
  id: number
  record_id: string
  owner_id?: number | null
  fields: Record<string, any>
  created_at: string
  updated_at: string
}
