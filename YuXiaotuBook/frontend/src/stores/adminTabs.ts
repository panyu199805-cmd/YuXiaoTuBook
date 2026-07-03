import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { RouteLocationNormalized } from 'vue-router'

export interface AdminTabItem {
  path: string
  title: string
}

export const useAdminTabsStore = defineStore('adminTabs', () => {
  const tabs = ref<AdminTabItem[]>([])

  function addTab(route: RouteLocationNormalized) {
    const title = route.meta.title as string | undefined
    if (!title) return
    if (!tabs.value.some((t) => t.path === route.path)) {
      tabs.value.push({ path: route.path, title })
    }
  }

  function removeTab(path: string) {
    const idx = tabs.value.findIndex((t) => t.path === path)
    if (idx === -1) return tabs.value[0]?.path || '/admin/books'
    tabs.value.splice(idx, 1)
    return tabs.value[idx]?.path || tabs.value[idx - 1]?.path || '/admin/books'
  }

  function clearTabs() {
    tabs.value = []
  }

  return { tabs, addTab, removeTab, clearTabs }
})
