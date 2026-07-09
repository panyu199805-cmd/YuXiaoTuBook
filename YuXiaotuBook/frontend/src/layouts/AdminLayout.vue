<script setup lang="ts">
import { computed, onMounted, ref, watch, type Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowDown, Close, Search } from '@element-plus/icons-vue'
import {
  adminMenuGroups,
  filterAdminMenu,
  findMenuGroupByPath,
  getAdminMenuItemIcon,
  isGroupActive,
  resolveAdminScope,
  searchMenuOptions,
  type AdminMenuSearchOption,
} from '@/config/adminMenu'
import { useAdminTabsStore } from '@/stores/adminTabs'
import { useUserStore } from '@/stores/user'
import { defaultAvatarImage, resolveAvatarUrl } from '@/utils/media'

const route = useRoute()
const router = useRouter()
const store = useUserStore()
const tabsStore = useAdminTabsStore()
const collapsed = ref(false)
const searchKey = ref('')

const menuGroups = computed(() =>
  filterAdminMenu(adminMenuGroups, resolveAdminScope(store.user?.username)),
)

const activeMenu = computed(() => route.path)
const openedMenus = ref<string[]>([])

const HOVER_OPEN_DELAY_MS = 320
let hoverOpenTimer: ReturnType<typeof setTimeout> | null = null

const pageTitle = computed(() => (route.meta.title as string) || '工作台')
const parentTitle = computed(() => (route.meta.parentTitle as string) || '')
const avatarLetter = computed(() => (store.user?.nickname || store.user?.username || '管').charAt(0))
const adminAvatarUrl = computed(() => {
  const remote = resolveAvatarUrl(store.user?.avatar)
  return remote || defaultAvatarImage(avatarLetter.value)
})
const adminDisplayName = computed(() => store.user?.nickname || store.user?.username || '管理员')

onMounted(() => {
  store.fetchMe()
})

const filteredMenuGroups = computed(() => menuGroups.value)

function ensureMenuOpened(path: string) {
  const matched = findMenuGroupByPath(path)
  if (!matched) return
  if (!openedMenus.value.includes(matched.group.key)) {
    openedMenus.value = [...openedMenus.value, matched.group.key]
  }
}

function handleMenuOpen(key: string) {
  if (!openedMenus.value.includes(key)) {
    openedMenus.value = [...openedMenus.value, key]
  }
}

function handleMenuClose(key: string) {
  openedMenus.value = openedMenus.value.filter((item) => item !== key)
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

function clearAllTabs() {
  tabsStore.clearTabs()
}

function resolveChildIcon(path: string, icon?: Component) {
  return icon || getAdminMenuItemIcon(path)
}

function navigateTo(path: string) {
  router.push(path)
}

function isChildActive(path: string) {
  return activeMenu.value === path
}

function openSubMenuOnHover(event: MouseEvent) {
  const subMenu = event.currentTarget as HTMLElement | null
  if (!subMenu?.classList.contains('el-sub-menu') || subMenu.classList.contains('is-opened')) return

  if (hoverOpenTimer) clearTimeout(hoverOpenTimer)

  hoverOpenTimer = setTimeout(() => {
    if (subMenu.classList.contains('is-opened')) return
    const title = subMenu.querySelector('.el-sub-menu__title') as HTMLElement | null
    title?.click()
    hoverOpenTimer = null
  }, HOVER_OPEN_DELAY_MS)
}

function cancelSubMenuHoverOpen() {
  if (!hoverOpenTimer) return
  clearTimeout(hoverOpenTimer)
  hoverOpenTimer = null
}

function expandSidebarFromGroup(groupKey: string) {
  if (!openedMenus.value.includes(groupKey)) {
    openedMenus.value = [...openedMenus.value, groupKey]
  }
  collapsed.value = false
}

function queryMenuSearch(queryString: string, cb: (results: AdminMenuSearchOption[]) => void) {
  cb(searchMenuOptions(menuGroups.value, queryString))
}

function onMenuSearchSelect(item: AdminMenuSearchOption) {
  searchKey.value = ''
  expandSidebarFromGroup(item.groupKey)
  navigateTo(item.path)
}

watch(
  () => route.path,
  (path) => {
    ensureMenuOpened(path)
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
        <div v-show="!collapsed" class="logo-copy">
          <span class="logo-text">宇小兔每日读书</span>
          <span class="logo-sub">后台管理系统</span>
        </div>
      </div>

      <nav class="nav-menu">
        <el-menu
          v-if="!collapsed"
          :default-active="activeMenu"
          :default-openeds="openedMenus"
          :collapse-transition="false"
          class="admin-side-menu"
          @open="handleMenuOpen"
          @close="handleMenuClose"
        >
          <el-sub-menu
            v-for="group in filteredMenuGroups"
            :key="group.key"
            :index="group.key"
            @mouseenter="openSubMenuOnHover"
            @mouseleave="cancelSubMenuHoverOpen"
          >
            <template #title>
              <el-icon><component :is="group.icon" /></el-icon>
              <span>{{ group.title }}</span>
            </template>
            <el-menu-item
              v-for="child in group.children"
              :key="child.path"
              :index="child.path"
              @click="navigateTo(child.path)"
            >
              <el-icon v-if="resolveChildIcon(child.path, child.icon)">
                <component :is="resolveChildIcon(child.path, child.icon)" />
              </el-icon>
              <span>{{ child.title }}</span>
            </el-menu-item>
          </el-sub-menu>
        </el-menu>

        <div v-else class="collapsed-nav">
          <el-popover
            v-for="group in filteredMenuGroups"
            :key="group.key"
            trigger="hover"
            :show-after="280"
            :hide-after="220"
            placement="right-start"
            :width="248"
            :show-arrow="false"
            :offset="6"
            popper-class="admin-flyout-popper"
          >
            <template #reference>
              <button
                type="button"
                class="collapsed-nav-item"
                :class="{ active: isGroupActive(group, activeMenu) }"
                :title="`${group.title}（双击展开侧栏）`"
                @dblclick="expandSidebarFromGroup(group.key)"
              >
                <el-icon :size="20"><component :is="group.icon" /></el-icon>
              </button>
            </template>

            <div class="flyout-panel">
              <div class="flyout-header">
                <span class="flyout-header-icon">
                  <el-icon :size="18"><component :is="group.icon" /></el-icon>
                </span>
                <span class="flyout-header-title">{{ group.title }}</span>
              </div>
              <div class="flyout-list">
                <button
                  v-for="child in group.children"
                  :key="child.path"
                  type="button"
                  class="flyout-item"
                  :class="{ active: isChildActive(child.path) }"
                  @click="navigateTo(child.path)"
                >
                  <span class="flyout-item-icon">
                    <el-icon :size="16">
                      <component :is="resolveChildIcon(child.path, child.icon)" />
                    </el-icon>
                  </span>
                  <span class="flyout-item-text">{{ child.title }}</span>
                </button>
              </div>
            </div>
          </el-popover>
        </div>
      </nav>
    </aside>

    <div class="main-wrapper">
      <header class="topbar">
        <div class="topbar-left">
          <el-tooltip :content="collapsed ? '展开菜单栏' : '折叠菜单栏'" placement="bottom" :show-after="280">
            <button
              type="button"
              class="sidebar-toggle-btn"
              :class="{ 'is-collapsed': collapsed }"
              :aria-label="collapsed ? '展开菜单栏' : '折叠菜单栏'"
              @click="collapsed = !collapsed"
            >
              <svg viewBox="0 0 24 24" class="sidebar-toggle-icon" aria-hidden="true">
                <rect x="3.5" y="4.5" width="17" height="15" rx="2.5" class="panel-frame" />
                <rect
                  x="5.5"
                  y="6.5"
                  :width="collapsed ? 2.2 : 4.8"
                  height="11"
                  rx="1"
                  class="panel-sidebar"
                />
                <line x1="12" y1="9" x2="18" y2="9" class="panel-line" />
                <line x1="12" y1="12" x2="16.5" y2="12" class="panel-line panel-line-short" />
                <line x1="12" y1="15" x2="18.5" y2="15" class="panel-line" />
              </svg>
            </button>
          </el-tooltip>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>宇小兔读书后台</el-breadcrumb-item>
            <el-breadcrumb-item v-if="parentTitle">{{ parentTitle }}</el-breadcrumb-item>
            <el-breadcrumb-item>{{ pageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="topbar-right">
          <el-autocomplete
            v-model="searchKey"
            class="search-autocomplete"
            popper-class="admin-menu-search-popper"
            placeholder="搜索菜单名称..."
            :fetch-suggestions="queryMenuSearch"
            :trigger-on-focus="false"
            :debounce="120"
            clearable
            value-key="value"
            @select="onMenuSearchSelect"
          >
            <template #prefix>
              <el-icon class="search-prefix-icon"><Search /></el-icon>
            </template>
            <template #default="{ item }">
              <div class="menu-search-item">
                <span class="menu-search-item-icon">
                  <el-icon :size="16">
                    <component :is="item.icon" />
                  </el-icon>
                </span>
                <div class="menu-search-item-copy">
                  <span class="menu-search-item-title">{{ item.title }}</span>
                  <span class="menu-search-item-group">{{ item.groupTitle }}</span>
                </div>
              </div>
            </template>
          </el-autocomplete>
          <el-dropdown
            class="user-dropdown"
            trigger="click"
            @command="(cmd: string) => cmd === 'logout' && logout()"
          >
            <div class="user-info">
              <el-avatar :size="32" :src="adminAvatarUrl" class="avatar" fit="cover">
                {{ avatarLetter }}
              </el-avatar>
              <span class="nickname">{{ adminDisplayName }}</span>
              <el-icon class="user-caret"><ArrowDown /></el-icon>
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
        <div class="tab-list">
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
          <button
            type="button"
            class="tab-item tab-clear-btn"
            title="清空已打开的菜单记录"
            @click="clearAllTabs"
          >
            清空记录
          </button>
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
  width: 248px;
  background: linear-gradient(180deg, #ffffff 0%, #f8faff 100%);
  border-right: 1px solid var(--ecms-border);
  display: flex;
  flex-direction: column;
  transition: width 0.25s;
  flex-shrink: 0;
}

.admin-layout.collapsed .sidebar {
  width: 72px;
}

.logo-area {
  height: 68px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 18px;
  border-bottom: 1px solid var(--ecms-border);
}

.logo-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--ecms-primary), #7c3aed);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 18px;
  flex-shrink: 0;
  box-shadow: 0 8px 20px rgba(93, 135, 255, 0.28);
}

.logo-copy {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.logo-text {
  font-size: 15px;
  font-weight: 700;
  color: var(--ecms-text);
  white-space: nowrap;
}

.logo-sub {
  font-size: 12px;
  color: var(--ecms-text-secondary);
  white-space: nowrap;
}

.nav-menu {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0 16px;
}

.admin-side-menu {
  border-right: none;
  background: transparent;
}

.collapsed-nav {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
}

.collapsed-nav-item {
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 12px;
  background: transparent;
  color: var(--ecms-sidebar-text);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.collapsed-nav-item:hover,
.collapsed-nav-item.active {
  background: var(--ecms-sidebar-active-bg);
  color: var(--ecms-primary);
  box-shadow: inset 0 0 0 1px rgba(93, 135, 255, 0.18);
}

.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.topbar {
  height: 60px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(10px);
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
  gap: 14px;
  flex: 1;
  min-width: 0;
}

.topbar-left :deep(.el-breadcrumb) {
  min-width: 0;
  overflow: hidden;
}

.sidebar-toggle-btn {
  width: 38px;
  height: 38px;
  border: 1px solid rgba(93, 135, 255, 0.16);
  border-radius: 10px;
  background: linear-gradient(180deg, #ffffff 0%, #f5f8ff 100%);
  color: var(--ecms-primary);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  padding: 0;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
  transition:
    border-color 0.2s ease,
    background 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease,
    color 0.2s ease;
}

.sidebar-toggle-btn:hover {
  color: #4670f0;
  border-color: rgba(93, 135, 255, 0.38);
  background: #fff;
  box-shadow: 0 6px 16px rgba(93, 135, 255, 0.14);
}

.sidebar-toggle-btn:active {
  transform: scale(0.96);
}

.sidebar-toggle-icon {
  width: 20px;
  height: 20px;
  display: block;
}

.panel-frame {
  fill: none;
  stroke: currentColor;
  stroke-width: 1.5;
}

.panel-sidebar {
  fill: currentColor;
  opacity: 0.24;
  transition: width 0.25s ease, opacity 0.25s ease;
}

.sidebar-toggle-btn.is-collapsed .panel-sidebar {
  opacity: 0.38;
}

.panel-line {
  stroke: currentColor;
  stroke-width: 1.5;
  stroke-linecap: round;
  opacity: 0.72;
  transition: opacity 0.2s ease, stroke-width 0.2s ease;
}

.sidebar-toggle-btn:hover .panel-line {
  opacity: 0.95;
}

.sidebar-toggle-btn:hover .panel-line-short {
  stroke-width: 1.7;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  margin-left: 20px;
}

.search-autocomplete {
  width: 200px;
  flex-shrink: 0;
}

.user-dropdown {
  flex-shrink: 0;
}

.search-autocomplete :deep(.el-input__wrapper) {
  border-radius: 999px;
  background: #f7f9ff;
  box-shadow: 0 0 0 1px rgba(93, 135, 255, 0.12) inset;
  transition: box-shadow 0.2s ease, background-color 0.2s ease;
}

.search-autocomplete :deep(.el-input__wrapper:hover),
.search-autocomplete :deep(.el-input__wrapper.is-focus) {
  background: #fff;
  box-shadow: 0 0 0 1px rgba(93, 135, 255, 0.28) inset;
}

.search-prefix-icon {
  color: var(--ecms-text-secondary);
  font-size: 16px;
}

.menu-search-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 2px 0;
}

.menu-search-item-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: rgba(93, 135, 255, 0.08);
  color: var(--ecms-primary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.menu-search-item-copy {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.menu-search-item-title {
  font-size: 13px;
  color: var(--ecms-text);
  line-height: 1.4;
}

.menu-search-item-group {
  font-size: 12px;
  color: var(--ecms-text-secondary);
  line-height: 1.3;
}

.user-info {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 10px 4px 4px;
  border-radius: 999px;
  border: 1px solid transparent;
  white-space: nowrap;
  flex-shrink: 0;
}

.user-info:hover {
  background: var(--ecms-sidebar-active-bg);
  border-color: rgba(93, 135, 255, 0.15);
}

.avatar {
  flex-shrink: 0;
  background: linear-gradient(135deg, var(--ecms-primary), #7c3aed);
  color: #fff;
  font-size: 14px;
}

.avatar :deep(img) {
  object-fit: cover;
}

.nickname {
  font-size: 14px;
  color: var(--ecms-text);
  line-height: 1;
  white-space: nowrap;
  max-width: 88px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-caret {
  flex-shrink: 0;
  font-size: 12px;
  color: var(--ecms-text-secondary);
}

.tab-bar {
  padding: 8px 16px;
  background: #fff;
  border-bottom: 1px solid var(--ecms-border);
  flex-shrink: 0;
}

.tab-list {
  display: flex;
  align-items: center;
  gap: 6px;
  overflow-x: auto;
  min-width: 0;
  padding-bottom: 2px;
}

.tab-list::-webkit-scrollbar {
  height: 4px;
}

.tab-list::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.12);
  border-radius: 999px;
}

.tab-clear-btn {
  flex-shrink: 0;
  color: var(--ecms-text-secondary);
}

.tab-clear-btn:hover {
  color: #e34d59;
  border-color: rgba(227, 77, 89, 0.35);
  background: rgba(227, 77, 89, 0.06);
}

.tab-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 13px;
  color: var(--ecms-text-secondary);
  cursor: pointer;
  white-space: nowrap;
  border: 1px solid var(--ecms-border);
  background: #fff;
  transition: all 0.15s;
  font-family: inherit;
  line-height: 1.4;
}

.tab-item:hover {
  color: var(--ecms-primary);
  border-color: rgba(93, 135, 255, 0.35);
}

.tab-item.active {
  color: var(--ecms-primary);
  background: var(--ecms-sidebar-active-bg);
  border-color: rgba(93, 135, 255, 0.35);
  font-weight: 600;
}

.tab-close {
  font-size: 12px;
  border-radius: 50%;
  padding: 1px;
}

.tab-close:hover {
  background: rgba(0, 0, 0, 0.08);
}

.content {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 18px;
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
