import type { RiskLevel } from '@/types/domain'

export function getRiskMeta(level: RiskLevel) {
  const map = {
    high: { label: '高风险', tone: 'danger', color: '#9A3412', backgroundColor: '#FFEDD5', surfaceColor: '#FFF7ED', borderColor: '#FDBA74' },
    medium: { label: '中风险', tone: 'warning', color: '#854D0E', backgroundColor: '#FEF3C7', surfaceColor: '#FFFBEB', borderColor: '#FDE68A' },
    low: { label: '低风险', tone: 'success', color: '#1E3A8A', backgroundColor: '#DBEAFE', surfaceColor: '#EFF6FF', borderColor: '#BFDBFE' },
    pending: { label: '未生成', tone: 'muted', color: '#334155', backgroundColor: '#E2E8F0', surfaceColor: '#FFFFFF', borderColor: '#E2E8F0' }
  } as const
  return map[level]
}

export function formatPercent(value: number) {
  return `${Math.round(value * 100)}%`
}
