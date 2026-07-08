import type {
  AdminNotificationRow,
  AdminOverview,
  AdminReportRow,
  AdminServiceRequestRow,
  AdminStats,
  AdminUserRow,
  AuthUser,
  DetectionFormInput,
  DetectionJob,
  DetectionReport,
  ModelConfigResponse,
  NotificationListResponse,
  SelectOption,
  ServiceAdviceReport,
  ServiceRequestInput,
  ServiceRequestItem,
} from '@/types/domain'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
let authToken = ''

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export function setAuthToken(token: string) {
  authToken = token
}

function withAuthHeaders(options?: RequestInit): RequestInit {
  const headers = new Headers(options?.headers)
  if (authToken) headers.set('Authorization', `Bearer ${authToken}`)
  return { ...options, headers }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, withAuthHeaders(options))
  if (!response.ok) {
    let detail = ''
    try {
      const body = await response.json() as { detail?: string }
      detail = body.detail ?? ''
    } catch {
      detail = ''
    }
    throw new ApiError(response.status, detail || `API request failed: ${response.status}`)
  }
  return response.json() as Promise<T>
}

export function getOptions() {
  return request<{ categories: SelectOption[]; markets: SelectOption[] }>('/api/options')
}

export function sendCode(mobile: string) {
  return request<{ ok: boolean; debugCode?: string | null }>('/api/auth/code', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ mobile }) })
}

export function loginWithPassword(mobile: string, password: string) {
  return request<{ ok: boolean; token: string; user: AuthUser | null }>('/api/auth/login', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ mobile, password }) })
}

export function loginWithCode(mobile: string, code: string) {
  return request<{ ok: boolean; token: string; user: AuthUser | null }>('/api/auth/login/code', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ mobile, code }) })
}

export function registerWithCode(mobile: string, code: string, password: string) {
  return request<{ ok: boolean; userId: number | null; token: string; user: AuthUser | null }>('/api/auth/register', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ mobile, code, password }) })
}

export function getMe() {
  return request<AuthUser>('/api/auth/me')
}

export function logout() {
  return request<{ ok: boolean }>('/api/auth/logout', { method: 'POST' })
}

export function getJobs() {
  return request<DetectionJob[]>('/api/jobs')
}

export function createJob(input: DetectionFormInput) {
  return request<{ jobId: string; input: DetectionFormInput }>('/api/jobs', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(input) })
}

export function uploadJobFile(jobId: string, file: File) {
  const body = new FormData()
  body.append('file', file)
  return request<{ jobId: string; fileUrl: string }>(`/api/jobs/${encodeURIComponent(jobId)}/upload`, { method: 'POST', body })
}

export function runJob(jobId: string) {
  return request<{ jobId: string; status: 'queued' }>(`/api/jobs/${encodeURIComponent(jobId)}/run`, { method: 'POST' })
}

export function requestJobReview(jobId: string, note = '') {
  return request<{ ok: boolean; jobId: string; reviewStatus: string }>(`/api/jobs/${encodeURIComponent(jobId)}/review`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ note }) })
}

export function getJobStatus(jobId: string) {
  return request<DetectionJob>(`/api/jobs/${encodeURIComponent(jobId)}/status`)
}

export function getJobResults(id: string) {
  return request<DetectionReport>(`/api/jobs/${encodeURIComponent(id)}/results`)
}

export function getReports() {
  return request<DetectionReport[]>('/api/reports')
}

export function getServiceRequests() {
  return request<ServiceRequestItem[]>('/api/service-requests')
}

export function createServiceRequest(input: ServiceRequestInput) {
  return request<{ ok: boolean; request: ServiceRequestItem; adviceReport: ServiceAdviceReport }>('/api/service-requests', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(input) })
}

export function getReport(id: string) {
  return request<DetectionReport>(`/api/reports/${encodeURIComponent(id)}`)
}

export function getAdminJobs() {
  return request<{ stats: AdminStats; jobs: DetectionJob[] }>('/api/admin/jobs')
}

export function getAdminOverview() {
  return request<AdminOverview>('/api/admin/overview')
}

export function getAdminUsers() {
  return request<AdminUserRow[]>('/api/admin/users')
}

export function getAdminReports() {
  return request<AdminReportRow[]>('/api/admin/reports')
}

export function getAdminServiceRequests() {
  return request<AdminServiceRequestRow[]>('/api/admin/service-requests')
}

export function getAdminNotifications() {
  return request<AdminNotificationRow[]>('/api/admin/notifications')
}

export function updateAdminJobReview(jobId: string, reviewStatus: 'approved' | 'rejected', reviewNote = '') {
  return request<DetectionJob>(`/api/admin/jobs/${encodeURIComponent(jobId)}/review`, { method: 'PATCH', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ reviewStatus, reviewNote }) })
}

export function getModelConfig() {
  return request<ModelConfigResponse>('/api/admin/model-config')
}

export function updateModelConfig(input: { provider: string; modelName: string; apiKey: string; baseUrl: string; temperature: number; maxTokens: number; enabled: boolean }) {
  return request<ModelConfigResponse>('/api/admin/model-config', { method: 'PUT', headers: { 'content-type': 'application/json' }, body: JSON.stringify(input) })
}

export function getNotifications() {
  return request<NotificationListResponse>('/api/notifications')
}

export function getUnreadNotificationCount() {
  return request<{ unreadCount: number }>('/api/notifications/unread-count')
}

export function markNotificationRead(notificationId: number) {
  return request<{ ok: boolean }>(`/api/notifications/${notificationId}/read`, { method: 'POST' })
}

function filenameFromDisposition(disposition: string | null, fallback: string) {
  if (!disposition) return fallback
  const utf8Match = disposition.match(/filename\*=UTF-8''([^;]+)/i)
  if (utf8Match?.[1]) return decodeURIComponent(utf8Match[1])
  const filenameMatch = disposition.match(/filename="?([^";]+)"?/i)
  return filenameMatch?.[1] ?? fallback
}

export async function downloadReportPdf(jobId: string) {
  const response = await fetch(`${API_BASE_URL}/api/jobs/${encodeURIComponent(jobId)}/report/pdf`, withAuthHeaders())
  if (!response.ok) throw new Error(`API request failed: ${response.status}`)
  const blob = await response.blob()
  return {
    blob,
    filename: filenameFromDisposition(response.headers.get('content-disposition'), `ip-report-${jobId}.pdf`)
  }
}
