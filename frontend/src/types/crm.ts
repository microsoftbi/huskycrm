export interface Account {
  id: string
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
  owner_id?: string
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
  owner_id?: string
}

export interface AccountUpdate extends Partial<AccountCreate> {}

export interface Contact {
  id: string
  first_name: string
  last_name: string
  email?: string
  phone?: string
  mobile_phone?: string
  title?: string
  department?: string
  account_id?: string
  account_name?: string
  accounts?: ContactAccount[]
  owner_id?: string
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
  account_id?: string
  owner_id?: string
}

export interface ContactUpdate extends Partial<ContactCreate> {}

export interface ContactAccount {
  id: string
  contact_id: string
  account_id: string
  account_name?: string
  assigned_at?: string
}

export interface ContactAccountCreate {
  account_id: string
}

export interface Product {
  id: string
  name: string
  product_code?: string
  description?: string
  price?: number
  cost?: number
  category?: string
  is_active?: boolean
  owner_id?: string
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
  owner_id?: string
}

export interface ProductUpdate extends Partial<ProductCreate> {}

export interface Stage {
  id: string
  name: string
  probability: number
  sort_order: number
  is_closed_won: boolean
  is_closed_lost: boolean
}

export interface Opportunity {
  id: string
  name: string
  account_id?: string
  stage_id: string
  amount?: number
  probability?: number
  close_date?: string
  description?: string
  owner_id?: string
  created_at: string
  updated_at: string
}

export interface OpportunityCreate {
  name: string
  account_id?: string
  stage_id: string
  amount?: number
  probability?: number
  close_date?: string
  description?: string
  owner_id?: string
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
  id: string
  opportunity_id: string
  product_id: string
  quantity: number
  unit_price: number
  total_price: number
  created_at: string
}

export interface LineItemCreate {
  product_id: string
  quantity: number
  unit_price: number
}

// ── Custom Objects ────────────────────────────────────────────────

export interface CustomFieldDef {
  id: string
  object_id: string
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
  lookup_object_id?: string | null
  display_order: number
  created_at: string
  updated_at: string
}

export interface CustomObjectDef {
  id: string
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
  lookup_object_id?: string | null
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
  id: string
  record_id: string
  owner_id?: string | null
  fields: Record<string, any>
  created_at: string
  updated_at: string
}
