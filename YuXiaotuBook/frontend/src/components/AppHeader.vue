<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const store = useUserStore()
const route = useRoute()
const router = useRouter()
const scrolled = ref(false)

const isHeroPage = computed(() => route.name === 'Home')
const heroOverlay = computed(() => isHeroPage.value && !scrolled.value)

function onScroll() {
  scrolled.value = window.scrollY > 280
}

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))

watch(
  () => route.name,
  () => {
    scrolled.value = false
  }
)
</script>

<template>
  <header class="header" :class="{ 'header--hero': heroOverlay }">
    <div class="container inner">
      <router-link to="/" class="brand">宇小兔每日读书</router-link>
      <nav class="nav">
        <router-link to="/">首页</router-link>
        <router-link to="/books">书单</router-link>
        <router-link to="/daily">每日读书</router-link>
        <router-link to="/member">会员中心</router-link>
      </nav>
      <div class="actions">
        <span v-if="store.isVip" class="vip-badge">VIP</span>
        <template v-if="store.isLoggedIn">
          <router-link to="/user/favorites">收藏</router-link>
          <router-link to="/user/history">浏览记录</router-link>
          <router-link to="/user/orders">订单</router-link>
          <router-link to="/user/center">个人中心</router-link>
          <button class="btn btn-outline btn-ghost" @click="store.logout(); router.push('/')">退出</button>
        </template>
        <template v-else>
          <router-link to="/login" class="btn btn-outline btn-ghost">登录</router-link>
          <router-link to="/register" class="btn btn-primary btn-solid">注册</router-link>
        </template>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header--hero {
  background: rgba(15, 23, 42, 0.28);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  color: #fff;
  transition: background 0.25s, color 0.25s, border-color 0.25s;
}

.header:not(.header--hero) {
  transition: background 0.25s, color 0.25s, border-color 0.25s;
}

.header--hero .brand {
  color: #fff;
}

.header--hero .nav a {
  color: rgba(255, 255, 255, 0.88);
}

.header--hero .nav a.router-link-active {
  color: #fff;
  font-weight: 600;
}

.header--hero .actions a {
  color: rgba(255, 255, 255, 0.88);
}

.header--hero .btn-ghost {
  border-color: rgba(255, 255, 255, 0.45);
  color: #fff;
}

.header--hero .btn-solid {
  background: rgba(255, 255, 255, 0.95);
  color: var(--color-primary);
}

.inner {
  display: flex;
  align-items: center;
  height: 64px;
  gap: 32px;
}

.brand {
  font-weight: 600;
  font-size: 18px;
  color: var(--color-primary);
}

.nav {
  display: flex;
  gap: 20px;
  flex: 1;
}

.nav a.router-link-active {
  color: var(--color-primary);
}

.actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.vip-badge {
  background: linear-gradient(135deg, #5d87ff, #7c3aed);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
}

@media (max-width: 767px) {
  .inner {
    gap: 12px;
    flex-wrap: wrap;
    height: auto;
    min-height: 64px;
    padding: 8px 0;
  }

  .nav {
    order: 3;
    width: 100%;
    overflow-x: auto;
    gap: 14px;
    padding-bottom: 4px;
  }

  .actions {
    margin-left: auto;
  }
}
</style>
