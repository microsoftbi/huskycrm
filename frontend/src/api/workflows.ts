import apiClient from './client'

export interface WorkflowActionConfig {
  action_type: string
  action_config: Record<string, any>
  display_order: number
}

export interface WorkflowRule {
  id: number
  name: string
  object_type: string
  trigger_event: string
  condition_expression?: any[] | null
  is_active: boolean
  actions: WorkflowActionConfig[]
  created_at: string
  updated_at: string
}

export interface WorkflowCreate {
  name: string
  object_type: string
  trigger_event: string
  condition_expression?: any[]
  actions: { action_type: string; action_config: Record<string, any>; display_order?: number }[]
}

export const workflowsApi = {
  list() { return apiClient.get<WorkflowRule[]>('/workflows') },
  get(id: number) { return apiClient.get<WorkflowRule>(`/workflows/${id}`) },
  create(data: WorkflowCreate) { return apiClient.post<WorkflowRule>('/workflows', data) },
  update(id: number, data: any) { return apiClient.put<WorkflowRule>(`/workflows/${id}`, data) },
  delete(id: number) { return apiClient.delete(`/workflows/${id}`) },
  test(id: number, record: any) { return apiClient.post(`/workflows/${id}/test`, { record }) },
  logs(id: number) { return apiClient.get(`/workflows/${id}/logs`) },
}

// ── Reports ──

export interface ReportDef {
  id: number
  name: string
  object_type: string
  report_type: string
  filters?: any[] | null
  grouping?: string[] | null
  aggregations?: any[] | null
  columns?: string[] | null
  owner_id?: number
  created_at: string
  updated_at: string
}

export interface ReportResult {
  columns: string[]
  rows: any[][]
  total: number
}

export const reportsApi = {
  list() { return apiClient.get<ReportDef[]>('/reports') },
  get(id: number) { return apiClient.get<ReportDef>(`/reports/${id}`) },
  create(data: any) { return apiClient.post<ReportDef>('/reports', data) },
  update(id: number, data: any) { return apiClient.put<ReportDef>(`/reports/${id}`, data) },
  delete(id: number) { return apiClient.delete(`/reports/${id}`) },
  run(id: number, params?: { page?: number; page_size?: number }) {
    return apiClient.post<ReportResult>(`/reports/${id}/run`, null, { params })
  },
}

// ── Dashboards ──

export interface DashboardComponent {
  id: number
  dashboard_id: number
  report_id: number
  title: string
  chart_type: string
  position_x: number
  position_y: number
  width: number
  height: number
}

export interface Dashboard {
  id: number
  name: string
  owner_id?: number
  components: DashboardComponent[]
  created_at: string
  updated_at: string
}

export const dashboardsApi = {
  list() { return apiClient.get<Dashboard[]>('/dashboards') },
  get(id: number) { return apiClient.get<Dashboard>(`/dashboards/${id}`) },
  create(data: { name: string }) { return apiClient.post<Dashboard>('/dashboards', data) },
  delete(id: number) { return apiClient.delete(`/dashboards/${id}`) },
  addComponent(dashboardId: number, data: any) {
    return apiClient.post(`/dashboards/${dashboardId}/components`, data)
  },
  deleteComponent(dashboardId: number, componentId: number) {
    return apiClient.delete(`/dashboards/${dashboardId}/components/${componentId}`)
  },
}