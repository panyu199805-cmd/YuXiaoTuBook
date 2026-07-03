<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowDown, Close, Fold } from '@element-plus/icons-vue'
import { adminMenuItems } from '@/config/adminMenu'
import { useAdminTabsStore } from '@/stores/adminTabs'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const store = useUserStore()
const tabsStore = useAdminTabsStore()
const collapsed = ref(false)
const searchKey = ref('')

const pageTitle = computed(() => (route.meta.title as string) || '工作台')
const avatarLetter = computed(() => (store.user?.nickname || '管').charAt(0))

function isActive(path: string, matchPrefix = false) {
  if (matchPrefix) return route.path === path || route.path.startsWith(path + '/')
  return route.path === path
}

function logout() {
  tabsStore.clearTabs()
  store.logout()
  router.push('/admin/login')
}

function closeTab(path: string) {
  const next = tabsStore.removeTab(path)
  if (route.path === path) router.push(next)
}

watch(
  () => route.path,
  () => {
    tabsStore.addTab(route)
  },
  { immediate: true },
)
</script>

<template>
  <div class="admin-layout admin-shell" :class="{ collapsed }" data-admin-theme="light">
    <aside class="sidebar">
      <div class="logo-area">
        <div class="logo-icon">宇</div>
        <span v-show="!collapsed" class="logo-text">宇小兔 · 管理</span>
      </div>
      <nav class="nav-menu">
        <router-link
          v-for="item in adminMenuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path, item.matchPrefix) }"
        >
          <el-icon :size="18"><component :is="item.icon" /></el-icon>
          <span v-show="!collapsed">{{ item.title }}</span>
        </router-link>
      </nav>
    </aside>

    <div class="main-wrapper">
      <header class="topbar">
        <div class="topbar-left">
          <el-icon class="collapse-btn" @click="collapsed = !collapsed"><Fold /></el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>仪表盘</el-breadcrumb-item>
            <el-breadcrumb-item>{{ pageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="topbar-right">
          <el-input
            v-model="searchKey"
            placeholder="搜索..."
            prefix-icon="Search"
            class="search-input"
            clearable
          />
          <el-dropdown trigger="click" @command="(cmd: string) => cmd === 'logout' && logout()">
            <div class="user-info">
              <el-avatar :size="32" class="avatar">{{ avatarLetter }}</el-avatar>
              <span class="nickname">{{ store.user?.nickname || '管理员' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <div v-if="tabsStore.tabs.length" class="tab-bar">
        <div
          v-for="tab in tabsStore.tabs"
          :key="tab.path"
          class="tab-item"
          :class="{ active: route.path === tab.path }"
          @click="router.push(tab.path)"
        >
          <span>{{ tab.title }}</span>
          <el-icon class="tab-close" @click.stop="closeTab(tab.path)"><Close /></el-icon>
        </div>
      </div>

      <main class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 240px;
  background: var(--ecms-sidebar-bg);
  border-right: 1px solid var(--ecms-border);
  display: flex;
  flex-direction: column;
  transition: width 0.25s;
  flex-shrink: 0;
}

.admin-layout.collapsed .sidebar {
  width: 64px;
}

.logo-area {
  height: 60px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 16px;
  border-bottom: 1px solid var(--ecms-border);
}

.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--ecms-primary), #7c3aed);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 18px;
  flex-shrink: 0;
}

.logo-text {
  font-size: 16px;
  font-weight: 700;
  color: var(--ecms-text);
  white-space: nowrap;
}

.nav-menu {
  padding: 12px 8px;
  flex: 1;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 14px;
  border-radius: var(--ecms-radius);
  color: var(--ecms-sidebar-text);
  text-decoration: none;
  font-size: 14px;
  margin-bottom: 4px;
  transition: all 0.2s;
  white-space: nowrap;
}

.nav-item:hover {
  background: var(--ecms-sidebar-active-bg);
  color: var(--ecms-primary);
}

.nav-item.active {
  background: var(--ecms-sidebar-active-bg);
  color: var(--ecms-primary);
  font-weight: 600;
}

.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.topbar {
  height: 56px;
  background: var(--ecms-header-bg);
  border-bottom: 1px solid var(--ecms-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  flex-shrink: 0;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: var(--ecms-text-secondary);
}

.collapse-btn:hover {
  color: var(--ecms-primary);
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-input {
  width: 200px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--ecms-radius);
}

.user-info:hover {
  background: var(--ecms-sidebar-active-bg);
}

.avatar {
  background: linear-gradient(135deg, var(--ecms-primary), #7c3aed);
  color: #fff;
  font-size: 14px;
}

.nickname {
  font-size: 14px;
  color: var(--ecms-text);
}

.tab-bar {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 16px;
  background: var(--ecms-header-bg);
  border-bottom: 1px solid var(--ecms-border);
  overflow-x: auto;
  flex-shrink: 0;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  border-radius: 6px;
  font-size: 13px;
  color: var(--ecms-text-secondary);
  cursor: pointer;
  white-space: nowrap;
  border: 1px solid transparent;
  transition: all 0.15s;
}

.tab-item:hover {
  color: var(--ecms-primary);
  background: var(--ecms-sidebar-active-bg);
}

.tab-item.active {
  color: var(--ecms-primary);
  background: var(--ecms-sidebar-active-bg);
  border-color: rgba(93, 135, 255, 0.3);
  font-weight: 500;
}

.tab-close {
  font-size: 12px;
  border-radius: 50%;
  padding: 1px;
}

.tab-close:hover {
  background: rgba(0, 0, 0, 0.1);
}

.content {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 16px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
