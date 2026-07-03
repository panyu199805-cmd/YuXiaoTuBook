<template>
  <div class="auth-brand">
    <div class="bg-layer">
      <div class="orb orb-1" />
      <div class="orb orb-2" />
      <div class="orb orb-3" />
      <div class="grid-pattern" />
    </div>

    <div class="brand-content">
      <div class="brand">
        <div class="brand-icon">
          <span>宇</span>
          <div class="icon-glow" />
        </div>
        <h1 class="main-title">宇小兔 · 内容管理后台</h1>
      </div>

      <p class="slogan">
        书籍、视频、分类与氛围配置一体化运营中台，助力每日读书内容高效发布与运营
      </p>

      <div class="feature-grid">
        <div v-for="item in features" :key="item.title" class="feature-card">
          <div class="feature-icon" :style="{ background: item.bg }">
            <el-icon :size="20"><component :is="item.icon" /></el-icon>
          </div>
          <div class="feature-body">
            <div class="feature-title">{{ item.title }}</div>
            <div class="feature-desc">{{ item.desc }}</div>
          </div>
        </div>
      </div>

      <p class="tech-stack">v1.0 | Vue3 前端 | FastAPI 后端 | MySQL 数据库</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Film, Menu as MenuIcon, Reading, Setting } from '@element-plus/icons-vue'

const features = [
  {
    title: '书籍内容管理',
    desc: '支持书籍新增、编辑、上下架与库存维护，快速构建每日读书书单。',
    icon: Reading,
    bg: 'rgba(93, 135, 255, 0.3)',
  },
  {
    title: '视频内容绑定',
    desc: '为每本书配置推荐视频，详情页一键播放，提升用户阅读体验。',
    icon: Film,
    bg: 'rgba(139, 92, 246, 0.28)',
  },
  {
    title: '分类体系运营',
    desc: '树形分类结构，支持成长、治愈、文学等多维度内容组织与筛选。',
    icon: MenuIcon,
    bg: 'rgba(0, 180, 42, 0.25)',
  },
  {
    title: '氛围与站点配置',
    desc: '首页背景、每日一句、精选书籍等氛围元素可视化配置，打造品牌感。',
    icon: Setting,
    bg: 'rgba(245, 158, 11, 0.25)',
  },
]
</script>

<style scoped>
.auth-brand {
  flex: 1;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  padding: 40px 48px;
  background: linear-gradient(145deg, #4a6cf7 0%, var(--ecms-primary, #5d87ff) 40%, #6d5ce8 75%, #7c3aed 100%);
}

.bg-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(64px);
  opacity: 0.45;
}

.orb-1 {
  width: 300px;
  height: 300px;
  background: #7dd3fc;
  top: -70px;
  right: -50px;
  animation: float 9s ease-in-out infinite;
}

.orb-2 {
  width: 220px;
  height: 220px;
  background: #a78bfa;
  bottom: 12%;
  left: -30px;
  animation: float 11s ease-in-out infinite reverse;
}

.orb-3 {
  width: 160px;
  height: 160px;
  background: #93c5fd;
  bottom: -30px;
  right: 28%;
  animation: float 8s ease-in-out infinite 0.5s;
}

.grid-pattern {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
  background-size: 36px 36px;
  mask-image: radial-gradient(ellipse 75% 65% at 45% 50%, black 15%, transparent 70%);
}

@keyframes float {
  0%,
  100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(10px, -14px);
  }
}

.brand-content {
  position: relative;
  z-index: 1;
  max-width: 580px;
  color: #fff;
  max-height: 100%;
  overflow-y: auto;
}

.brand {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  margin-bottom: 16px;
}

.brand-icon {
  position: relative;
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.16);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.22);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  font-weight: 800;
  flex-shrink: 0;
  margin-top: 4px;
}

.icon-glow {
  position: absolute;
  inset: -3px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.12);
  filter: blur(6px);
  z-index: -1;
}

.main-title {
  font-size: 26px;
  font-weight: 800;
  letter-spacing: -0.3px;
  margin: 0;
  line-height: 1.35;
}

.slogan {
  font-size: 15px;
  line-height: 1.7;
  opacity: 0.9;
  margin: 0 0 22px;
}

.feature-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 24px;
}

.feature-card {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 14px;
  border-radius: 13px;
  background: rgba(255, 255, 255, 0.09);
  backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.14);
  transition: transform 0.2s, background 0.2s;
}

.feature-card:hover {
  transform: translateY(-1px);
  background: rgba(255, 255, 255, 0.13);
}

.feature-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #fff;
}

.feature-title {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 5px;
  line-height: 1.3;
}

.feature-desc {
  font-size: 11px;
  opacity: 0.78;
  line-height: 1.55;
}

.tech-stack {
  font-size: 11px;
  opacity: 0.72;
  margin: 0;
  letter-spacing: 0.2px;
  line-height: 1.5;
}

@media (max-width: 1200px) {
  .feature-grid {
    grid-template-columns: 1fr;
  }

  .main-title {
    font-size: 22px;
  }
}

@media (max-width: 768px) {
  .auth-brand {
    display: none;
  }
}
</style>
