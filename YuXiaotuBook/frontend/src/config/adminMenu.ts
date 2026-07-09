import type { Component } from 'vue'
import {
  Calendar,
  Collection,
  DataAnalysis,
  DataBoard,
  DataLine,
  Document,
  Film,
  FolderOpened,
  Headset,
  Key,
  List,
  Location,
  Lock,
  MagicStick,
  Medal,
  Menu as MenuIcon,
  Monitor,
  PieChart,
  Picture,
  Reading,
  RefreshLeft,
  Setting,
  ShoppingCart,
  TrendCharts,
  User,
  Van,
  View,
} from '@element-plus/icons-vue'

export interface AdminMenuItem {
  path: string
  title: string
  icon?: Component
  matchPrefix?: boolean
}

export interface AdminMenuGroup {
  key: string
  title: string
  icon: Component
  children: AdminMenuItem[]
}

export interface AdminMenuSearchOption {
  value: string
  path: string
  title: string
  groupKey: string
  groupTitle: string
  icon: Component
}

const analyticsChildren: AdminMenuItem[] = [
  { path: '/admin/analytics/overview', title: '全站总览仪表盘', icon: DataAnalysis },
  { path: '/admin/analytics/reading', title: '用户阅读行为分析', icon: TrendCharts },
  { path: '/admin/analytics/orders', title: '交易订单数据统计', icon: PieChart },
  { path: '/admin/analytics/region', title: '用户地域分布分析', icon: Location },
  { path: '/admin/analytics/system', title: '系统性能监控面板', icon: Monitor },
]

const bookChildren: AdminMenuItem[] = [
  { path: '/admin/book/list', title: '书籍列表', icon: Reading, matchPrefix: true },
  { path: '/admin/book/category', title: '书籍分类', icon: MenuIcon },
  { path: '/admin/book/assets', title: '图书素材库', icon: FolderOpened },
  { path: '/admin/book/collections', title: '书单管理', icon: Collection },
]

const contentChildren: AdminMenuItem[] = [
  { path: '/admin/content/video', title: '解读视频管理', icon: Film },
  { path: '/admin/content/daily', title: '每日读书专栏', icon: Calendar },
  { path: '/admin/content/ai', title: 'AI 内容生成', icon: MagicStick },
  { path: '/admin/content/review', title: '内容审核', icon: View },
]

const atmosphereChildren: AdminMenuItem[] = [
  { path: '/admin/atmosphere/home', title: '首页氛围配置', icon: Setting },
  { path: '/admin/atmosphere/audio', title: '音噪素材管理', icon: Headset },
  { path: '/admin/atmosphere/global', title: '页面全局设置', icon: Picture },
]

const memberChildren: AdminMenuItem[] = [
  { path: '/admin/member/package', title: '会员套餐配置', icon: Medal },
  { path: '/admin/member/users', title: '用户会员列表', icon: User },
  { path: '/admin/member/stats', title: '会员权益统计', icon: DataLine },
  { path: '/admin/member/orders', title: '会员订单流水', icon: List },
]

const orderChildren: AdminMenuItem[] = [
  { path: '/admin/order/all', title: '全部订单列表', icon: ShoppingCart },
  { path: '/admin/order/aftersale', title: '售后订单管理', icon: RefreshLeft },
  { path: '/admin/order/stats', title: '销量数据统计', icon: DataBoard },
  { path: '/admin/order/logistics', title: '物流配置', icon: Van },
]

const permissionChildren: AdminMenuItem[] = [
  { path: '/admin/permission/user', title: '用户管理', icon: User },
  { path: '/admin/permission/role', title: '角色权限配置', icon: Key },
  { path: '/admin/permission/audit', title: '操作审计日志', icon: Document },
  { path: '/admin/permission/security', title: '系统安全配置', icon: Lock },
]

export const adminMenuGroups: AdminMenuGroup[] = [
  { key: 'analytics', title: '数据分析', icon: DataAnalysis, children: analyticsChildren },
  { key: 'book', title: '书籍管理', icon: Reading, children: bookChildren },
  { key: 'content', title: '内容管理', icon: Film, children: contentChildren },
  { key: 'atmosphere', title: '氛围配置', icon: Setting, children: atmosphereChildren },
  { key: 'member', title: '会员管理', icon: Medal, children: memberChildren },
  { key: 'order', title: '订单管理', icon: ShoppingCart, children: orderChildren },
  { key: 'permission', title: '权限管理', icon: User, children: permissionChildren },
]

function flattenMenuItems(groups: AdminMenuGroup[]): AdminMenuItem[] {
  return groups.flatMap((group) => group.children)
}

export const adminMenuItems: AdminMenuItem[] = flattenMenuItems(adminMenuGroups)

export const adminPageIcons: Record<string, Component> = Object.fromEntries(
  adminMenuItems
    .filter((item) => item.icon)
    .map((item) => [item.path, item.icon as Component]),
)

function isPathActive(item: AdminMenuItem, activePath: string): boolean {
  if (activePath === item.path) return true
  return Boolean(item.matchPrefix && activePath.startsWith(item.path))
}

export function resolveAdminScope(_username?: string | null): string {
  return 'all'
}

export function filterAdminMenu(groups: AdminMenuGroup[], _scope: string): AdminMenuGroup[] {
  return groups
}

export function findMenuGroupByPath(path: string): { group: AdminMenuGroup; child?: AdminMenuItem } | null {
  for (const group of adminMenuGroups) {
    for (const child of group.children) {
      if (isPathActive(child, path)) {
        return { group, child }
      }
    }
  }
  return null
}

export function getAdminMenuItemIcon(path: string): Component | undefined {
  return adminPageIcons[path]
}

export function isGroupActive(group: AdminMenuGroup, activePath: string): boolean {
  return group.children.some((child) => isPathActive(child, activePath))
}

export function searchMenuOptions(groups: AdminMenuGroup[], query: string): AdminMenuSearchOption[] {
  const keyword = query.trim().toLowerCase()
  if (!keyword) return []

  const results: AdminMenuSearchOption[] = []
  for (const group of groups) {
    for (const child of group.children) {
      const haystack = `${group.title} ${child.title}`.toLowerCase()
      if (!haystack.includes(keyword)) continue

      results.push({
        value: child.path,
        path: child.path,
        title: child.title,
        groupKey: group.key,
        groupTitle: group.title,
        icon: child.icon || group.icon,
      })
    }
  }
  return results
}
