type RuntimeImportMeta = ImportMeta & {
  env?: {
    VITE_API_BASE_URL?: string
  }
}

export function normalizeApiBaseUrl(value: string | undefined) {
  return value ?? ''
}

export const API_BASE_URL = normalizeApiBaseUrl((import.meta as RuntimeImportMeta).env?.VITE_API_BASE_URL)
