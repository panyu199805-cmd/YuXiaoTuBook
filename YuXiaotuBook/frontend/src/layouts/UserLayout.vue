<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import FloatSupportButton from '@/components/FloatSupportButton.vue'

const route = useRoute()
const isHome = computed(() => route.name === 'Home')
</script>

<template>
  <div class="user-layout" :class="{ 'user-layout--home': isHome }">
    <AppHeader />
    <main class="main">
      <router-view v-slot="{ Component }">
        <keep-alive include="Home">
          <component :is="Component" v-if="Component" />
        </keep-alive>
      </router-view>
    </main>
    <AppFooter />
    <FloatSupportButton />
  </div>
</template>

<style scoped>
.main {
  min-height: calc(100vh - 120px);
  padding-bottom: 48px;
}

.user-layout--home .main {
  padding-bottom: 32px;
}
</style>
