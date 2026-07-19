export interface ImportPreview {
  preview_id: string
  columns: string[]
  mapping_suggestions: Record<string, string | null>
  available_fields: { name: string; label: string; type: string; required: boolean }[]
  preview_rows: string[][]
}

export interface ImportConfirmRequest {
  preview_id: string
  mapping: Record<string, string>
}

export interface ImportResult {
  success_rows: number
  error_rows: number
  errors: { row: number; error: string }[]
}

export interface ImportJob {
  id: string
  object_type: string
  filename: string
  total_rows: number
  success_rows: number
  error_rows: number
  errors: string | null
  status: string
  created_by: string
  created_at: string | null
}