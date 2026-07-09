import { request } from '@/api/client'

export interface DashboardSummary {
  books: { total: number; published: number; draft: number }
  users: { total: number; today: number }
  orders: {
    today_count: number
    today_amount: number
    total_count: number
    total_amount: number
  }
  videos: { total: number; play_count: number }
  collects: { total: number; today: number }
  members: { vip_active: number; package_count: number; orders_today: number }
  daily: { total: number }
}

export interface DashboardOverview {
  summary: DashboardSummary
  book_status: { published: number; draft: number }
  category_distribution: Array<{ name: string; count: number }>
  order_trend: Array<{ date: string; count: number; amount?: number }>
  user_trend: Array<{ date: string; count: number }>
  top_books: Array<{
    id: number
    title: string
    cover: string
    view_count: number
    play_count: number
  }>
  recent_orders: Array<{
    id: number
    order_no: string
    user_nickname: string
    total_amount: number
    status: string
    status_label: string
    created_at: string | null
    book_summary: string
  }>
  order_status: Array<{ status: string; label: string; count: number }>
}

export interface ReadingStats {
  summary: {
    total_views: number
    total_plays: number
    favorite_total: number
    history_total: number
    daily_total: number
  }
  video_ranking: Array<{
    id: number
    title: string
    cover: string
    view_count: number
    play_count: number
    favorite_count: number
    history_count: number
  }>
  preference_stats: Array<{ name: string; count: number }>
  daily_stats: Array<{
    id: number
    title: string
    publish_date: string
    like_count: number
    is_top: boolean
  }>
  hour_distribution: Array<{ hour: number; count: number }>
}

export interface OrderStats {
  summary: {
    book_order_total: number
    book_revenue: number
    member_order_total: number
    member_revenue: number
    cancelled_total: number
  }
  order_trend: Array<{ date: string; count: number }>
  amount_trend: Array<{ date: string; amount: number }>
  member_trend: Array<{ date: string; count: number; amount: number }>
  status_stats: Array<{ status: string; label: string; count: number }>
  member_status_stats: Array<{ status: string; count: number }>
  top_sales: Array<{ id: number; title: string; quantity: number; amount: number }>
  hour_distribution: Array<{ hour: number; count: number }>
}

export interface RegionStats {
  summary: {
    province_count: number
    user_total: number
    filled_region_users: number
  }
  province_stats: Array<{
    province: string
    user_count: number
    order_count: number
    order_amount: number
    top_categories: Array<{ name: string; count: number }>
  }>
  city_stats: Array<{ city: string; user_count: number }>
}

export interface SystemStats {
  summary: {
    service: string
    status: string
    uptime_seconds: number
    db_status: string
    db_latency_ms: number
  }
  resources: {
    memory: { memory_total_mb?: number; memory_used_percent?: number }
    disk: { total_gb?: number; used_percent?: number }
    load_avg: string[]
  }
  table_counts: Record<string, number>
  notes: string[]
}

export function fetchDashboardOverview() {
  return request<DashboardOverview>({ url: '/admin/stats/overview', method: 'GET' })
}

export function fetchReadingStats() {
  return request<ReadingStats>({ url: '/admin/stats/reading', method: 'GET' })
}

export function fetchOrderStats(days = 30) {
  return request<OrderStats>({ url: '/admin/stats/orders', method: 'GET', params: { days } })
}

export function fetchRegionStats() {
  return request<RegionStats>({ url: '/admin/stats/region', method: 'GET' })
}

export function fetchSystemStats() {
  return request<SystemStats>({ url: '/admin/stats/system', method: 'GET' })
}
