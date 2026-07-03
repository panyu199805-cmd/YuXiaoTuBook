import type { Component } from 'vue'
import { Film, Menu as MenuIcon, Reading, Setting, ShoppingCart, Calendar, Medal, User } from '@element-plus/icons-vue'

export interface AdminMenuItem {
  path: string
  title: string
  icon: Component
  matchPrefix?: boolean
}

export const adminMenuItems: AdminMenuItem[] = [
  { path: '/admin/books', title: '书籍管理', icon: Reading, matchPrefix: true },
  { path: '/admin/videos', title: '视频管理', icon: Film },
  { path: '/admin/categories', title: '分类管理', icon: MenuIcon },
  { path: '/admin/orders', title: '订单管理', icon: ShoppingCart },
  { path: '/admin/users', title: '用户管理', icon: User },
  { path: '/admin/daily', title: '每日读书', icon: Calendar },
  { path: '/admin/member', title: '会员套餐', icon: Medal },
  { path: '/admin/site-config', title: '氛围配置', icon: Setting },
]
