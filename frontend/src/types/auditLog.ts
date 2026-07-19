export interface TimelineEntry {
  type: 'audit' | 'event' | 'task'
  action?: string
  field_name?: string
  old_value?: string
  new_value?: string
  subject?: string
  status?: string
  result?: string
  user_id?: string
  user_display_name?: string
  created_at?: string
  reference_id?: string
  reference_type?: string
}