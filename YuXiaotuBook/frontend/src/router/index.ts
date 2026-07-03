import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('@/layouts/UserLayout.vue'),
      children: [
        { path: '', name: 'Home', component: () => import('@/views/Home.vue') },
        { path: 'books', name: 'Books', component: () => import('@/views/Books.vue') },
        { path: 'books/:id', name: 'BookDetail', component: () => import('@/views/BookDetail.vue') },
        { path: 'daily', name: 'Daily', component: () => import('@/views/Daily.vue') },
        { path: 'member', name: 'Member', component: () => import('@/views/member/MemberCenter.vue') },
        { path: 'login', name: 'Login', component: () => import('@/views/Login.vue') },
        { path: 'register', name: 'Register', component: () => import('@/views/Register.vue') },
        {
          path: 'user/orders',
          name: 'UserOrders',
          meta: { login: true },
          component: () => import('@/views/user/Orders.vue'),
        },
        {
          path: 'user/favorites',
          name: 'UserFavorites',
          meta: { login: true },
          component: () => import('@/views/user/Favorites.vue'),
        },
        {
          path: 'user/history',
          name: 'UserHistory',
          meta: { login: true },
          component: () => import('@/views/user/History.vue'),
        },
        {
          path: 'user/center',
          name: 'UserCenter',
          meta: { login: true },
          component: () => import('@/views/user/UserCenter.vue'),
        },
      ],
    },
    {
      path: '/admin/login',
      name: 'AdminLogin',
      component: () => import('@/views/admin/Login.vue'),
    },
    {
      path: '/admin',
      component: () => import('@/layouts/AdminLayout.vue'),
      meta: { admin: true },
      children: [
        { path: '', redirect: '/admin/books' },
        { path: 'books', meta: { title: '书籍管理' }, component: () => import('@/views/admin/Books.vue') },
        { path: 'videos', meta: { title: '视频管理' }, component: () => import('@/views/admin/Videos.vue') },
        { path: 'categories', meta: { title: '分类管理' }, component: () => import('@/views/admin/Categories.vue') },
        { path: 'orders', meta: { title: '订单管理' }, component: () => import('@/views/admin/Orders.vue') },
        { path: 'users', meta: { title: '用户管理' }, component: () => import('@/views/admin/Users.vue') },
        { path: 'daily', meta: { title: '每日读书' }, component: () => import('@/views/admin/Daily.vue') },
        { path: 'member', meta: { title: '会员套餐' }, component: () => import('@/views/admin/MemberPackages.vue') },
        { path: 'site-config', meta: { title: '氛围配置' }, component: () => import('@/views/admin/SiteConfig.vue') },
      ],
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const store = useUserStore()
  if (to.meta.login && !store.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }
  if (to.meta.admin || to.path.startsWith('/admin')) {
    if (to.name === 'AdminLogin') {
      next()
      return
    }
    if (!store.isLoggedIn || !store.isAdmin) {
      next({ name: 'AdminLogin' })
      return
    }
  }
  next()
})

export default router
