export interface Event {
  id: string
  subject: string
  type: string
  status: string           // planned / in_progress / completed / cancelled
  start_datetime: string
  end_datetime?: string
  is_all_day_event?: boolean
  show_as?: string
  actual_start_time?: string
  actual_end_time?: string
  duration_minutes?: number
  what_id?: string | null
  what_type?: string | null
  who_id?: string | null
  owner_id?: string | null
  purpose?: string
  preparation_notes?: string
  description?: string
  outcome?: string          // success / neutral / failure / no_show
  next_steps?: string
  location?: string
  created_at: string
  updated_at: string
  tasks?: Task[]
}

export interface EventCreate {
  subject: string
  type?: string
  status?: string
  start_datetime: string
  end_datetime?: string
  is_all_day_event?: boolean
  show_as?: string
  what_id?: string | null
  what_type?: string | null
  who_id?: string | null
  owner_id?: string | null
  purpose?: string
  preparation_notes?: string
  description?: string
  outcome?: string
  next_steps?: string
  location?: string
}

export interface EventUpdate extends Partial<EventCreate> {}

export interface Task {
  id: string
  event_id: string
  subject: string
  status: string           // not_started / in_progress / completed / deferred
  priority: string         // high / normal / low
  activity_date?: string
  what_id?: string | null
  what_type?: string | null
  who_id?: string | null
  assignee_id?: string | null
  description?: string
  sort_order: number
  created_at: string
  updated_at: string
}

export interface TaskCreate {
  subject: string
  status?: string
  priority?: string
  activity_date?: string
  what_id?: string | null
  what_type?: string | null
  who_id?: string | null
  assignee_id?: string | null
  description?: string
  sort_order?: number
}

export interface TaskUpdate extends Partial<TaskCreate> {}
