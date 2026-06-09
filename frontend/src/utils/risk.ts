import type { RiskLevel } from '@/types/domain'

export function getRiskMeta(level: RiskLevel) {
  const map = {
    high: { label: '高风险', tone: 'danger', color: '#EF4444' },
    medium: { label: '中风险', tone: 'warning', color: '#F59E0B' },
    low: { label: '低风险', tone: 'success', color: '#22C55E' },
    pending: { label: '未生成', tone: 'muted', color: '#94A3B8' }
  } as const
  return map[level]
}

export function formatPercent(value: number) {
  return `${Math.round(value * 100)}%`
}
