import type { AdminStats, DetectionFormInput, DetectionJob, DetectionReport, SelectOption } from '@/types/domain'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, options)
  if (!response.ok) throw new Error(`API request failed: ${response.status}`)
  return response.json() as Promise<T>
}

export function getOptions() {
  return request<{ categories: SelectOption[]; markets: SelectOption[] }>('/api/options')
}

export function sendCode(mobile: string) {
  return request<{ ok: boolean }>('/api/auth/code', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ mobile }) })
}

export function loginWithCode(mobile: string, code: string) {
  return request<{ ok: boolean; token: string; user: { id: number; name: string } }>('/api/auth/login', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ mobile, code }) })
}

export function registerWithCode(mobile: string, code: string) {
  return request<{ ok: boolean }>('/api/auth/register', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ mobile, code }) })
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

export function getJobResults(id: string) {
  return request<DetectionReport>(`/api/jobs/${encodeURIComponent(id)}/results`)
}

export function getReports() {
  return request<DetectionReport[]>('/api/reports')
}

export function getReport(id: string) {
  return request<DetectionReport>(`/api/reports/${encodeURIComponent(id)}`)
}

export function getAdminJobs() {
  return request<{ stats: AdminStats; jobs: DetectionJob[] }>('/api/admin/jobs')
}

export function downloadReportUrl(jobId: string) {
  return `${API_BASE_URL}/api/jobs/${encodeURIComponent(jobId)}/report/pdf`
}
