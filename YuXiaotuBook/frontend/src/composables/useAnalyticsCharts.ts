export function formatNumber(value: number) {
  return value.toLocaleString('zh-CN')
}

export function formatMoney(value: number) {
  return value.toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

export function formatShortDate(iso: string) {
  const [, month, day] = iso.split('-')
  return `${month}/${day}`
}

export function formatDuration(seconds: number) {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  if (hours > 0) return `${hours}小时${minutes}分`
  return `${minutes}分钟`
}

export interface TrendPoint {
  date?: string
  hour?: number
  count?: number
  amount?: number
}

export function buildTrendChart(
  points: TrendPoint[],
  key: 'count' | 'amount',
  width = 360,
  height = 140,
) {
  const padding = { top: 16, right: 12, bottom: 28, left: 12 }
  const innerW = width - padding.left - padding.right
  const innerH = height - padding.top - padding.bottom
  const values = points.map((point) => Number(point[key] || 0))
  const max = Math.max(...values, 1)

  const coords = points.map((point, index) => {
    const x = padding.left + (index / Math.max(points.length - 1, 1)) * innerW
    const y = padding.top + innerH - (Number(point[key] || 0) / max) * innerH
    return { x, y, ...point }
  })

  const line = coords.map((coord) => `${coord.x},${coord.y}`).join(' ')
  const area = [
    `M ${coords[0]?.x ?? padding.left} ${padding.top + innerH}`,
    ...coords.map((coord) => `L ${coord.x} ${coord.y}`),
    `L ${coords[coords.length - 1]?.x ?? padding.left} ${padding.top + innerH}`,
    'Z',
  ].join(' ')

  return { width, height, coords, line, area, max }
}

export function buildBarRatios<T extends { count: number }>(items: T[]) {
  const max = Math.max(...items.map((item) => item.count), 1)
  return items.map((item) => ({
    ...item,
    ratio: (item.count / max) * 100,
  }))
}

export function hourLabel(hour: number) {
  return `${String(hour).padStart(2, '0')}:00`
}
