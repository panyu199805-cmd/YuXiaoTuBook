<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { adminPageIcons } from '@/config/adminMenu'

const route = useRoute()

const title = computed(() => (route.meta.title as string) || '功能开发中')
const desc = computed(() => (route.meta.placeholderDesc as string) || '该模块正在规划中，后续版本将接入完整业务能力。')
const features = computed(() => (route.meta.placeholderFeatures as string[] | undefined) || [])
const icon = computed(() => adminPageIcons[route.path])
</script>

<template>
  <div class="page-card placeholder-page">
    <div class="placeholder-icon" v-if="icon">
      <el-icon :size="36"><component :is="icon" /></el-icon>
    </div>
    <h2>{{ title }}</h2>
    <p class="desc">{{ desc }}</p>
    <ul v-if="features.length" class="feature-list">
      <li v-for="item in features" :key="item">{{ item }}</li>
    </ul>
    <el-tag type="info" effect="plain">即将上线</el-tag>
  </div>
</template>

<style scoped>
.placeholder-page {
  min-height: 360px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 12px;
}

.placeholder-icon {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(93, 135, 255, 0.12), rgba(124, 58, 237, 0.1));
  color: var(--ecms-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--ecms-text);
}

.desc {
  max-width: 520px;
  color: var(--ecms-text-secondary);
  line-height: 1.7;
}

.feature-list {
  max-width: 520px;
  text-align: left;
  margin: 4px 0 0;
  padding: 14px 18px;
  background: rgba(93, 135, 255, 0.06);
  border: 1px solid rgba(93, 135, 255, 0.12);
  border-radius: 10px;
  color: var(--ecms-text-secondary);
  line-height: 1.8;
  font-size: 14px;
}

.feature-list li + li {
  margin-top: 4px;
}
</style>
