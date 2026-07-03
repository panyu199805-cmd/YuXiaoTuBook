import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { request } from '@/api/client'

export interface UserInfo {
  id: number
  username: string
  nickname: string
  role: string
  avatar?: string
  is_vip?: boolean
  vip_expire_time?: string | null
}

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref<UserInfo | null>(
    localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')!) : null
  )
  const isVip = ref(user.value?.is_vip ?? false)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  function setAuth(t: string, u: UserInfo) {
    token.value = t
    user.value = u
    isVip.value = u.is_vip ?? false
    localStorage.setItem('token', t)
    localStorage.setItem('user', JSON.stringify(u))
  }

  function logout() {
    token.value = ''
    user.value = null
    isVip.value = false
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  async function fetchMe() {
    if (!token.value) return
    const res = await request<UserInfo>({ url: '/auth/me', method: 'GET' })
    if (res.code === 200) {
      user.value = res.data
      isVip.value = res.data.is_vip ?? false
      localStorage.setItem('user', JSON.stringify(res.data))
    }
  }

  return { user, isVip, isLoggedIn, isAdmin, setAuth, logout, fetchMe }
})
