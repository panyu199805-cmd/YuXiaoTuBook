<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { fetchSystemStats, type SystemStats } from '@/api/adminStats'
import { formatDuration, formatNumber } from '@/composables/useAnalyticsCharts'

const loading = ref(true)
const data = ref<SystemStats | null>(null)
let timer: ReturnType<typeof setInterval> | null = null

const tableRows = computed(() => {
  const counts = data.value?.table_counts || {}
  return Object.entries(counts).map(([name, count]) => ({ name, count }))
})

async function loadData() {
  try {
    const res = await fetchSystemStats()
    if (res.code === 200) data.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void loadData()
  timer = setInterval(loadData, 30000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div v-loading="loading" class="analytics-page">
    <header class="page-hero">
      <div>
        <h1>系统性能监控面板</h1>
        <p>展示 API 服务健康状态、容器资源占用与核心业务表数据量（单机 Docker 可观测范围）。</p>
      </div>
    </header>

    <div v-if="data" class="metric-grid">
      <div class="metric-item">
        <span>服务状态</span>
        <strong :class="data.summary.status === 'ok' ? 'status-ok' : 'status-warn'">
          {{ data.summary.status === 'ok' ? '运行正常' : '部分异常' }}
        </strong>
      </div>
      <div class="metric-item">
        <span>运行时长</span>
        <strong>{{ formatDuration(data.summary.uptime_seconds) }}</strong>
      </div>
      <div class="metric-item">
        <span>数据库探活</span>
        <strong>{{ data.summary.db_latency_ms }} ms</strong>
      </div>
      <div class="metric-item">
        <span>内存占用</span>
        <strong>{{ data.resources.memory.memory_used_percent ?? '—' }}%</strong>
      </div>
      <div class="metric-item">
        <span>磁盘占用</span>
        <strong>{{ data.resources.disk.used_percent ?? '—' }}%</strong>
      </div>
      <div class="metric-item">
        <span>系统负载</span>
        <strong>{{ data.resources.load_avg.join(' / ') || '—' }}</strong>
      </div>
    </div>

    <div class="panel-grid">
      <section class="panel-card">
        <div class="panel-header"><h3>资源详情</h3><p>来自 API 容器 /proc 读取</p></div>
        <ul class="detail-list">
          <li>总内存：{{ data?.resources.memory.memory_total_mb ?? '—' }} MB</li>
          <li>磁盘总量：{{ data?.resources.disk.total_gb ?? '—' }} GB</li>
          <li>数据库状态：{{ data?.summary.db_status === 'ok' ? '连接正常' : '连接异常' }}</li>
          <li>服务标识：{{ data?.summary.service }}</li>
        </ul>
      </section>

      <section class="panel-card">
        <div class="panel-header"><h3>业务表数据量</h3><p>反映当前系统业务负载</p></div>
        <el-table :data="tableRows" size="small">
          <el-table-column label="数据表" prop="name" />
          <el-table-column label="记录数" width="120">
            <template #default="{ row }">{{ formatNumber(row.count) }}</template>
          </el-table-column>
        </el-table>
      </section>

      <section class="panel-card span-2">
        <div class="panel-header"><h3>说明</h3><p>当前阶段监控能力边界</p></div>
        <ul class="note-list">
          <li v-for="note in data?.notes || []" :key="note">{{ note }}</li>
        </ul>
      </section>
    </div>
  </div>
</template>

<style scoped>
@import './analytics-shared.css';

.detail-list {
  margin: 0;
  padding-left: 18px;
  line-height: 2;
  color: var(--ecms-text-secondary);
  font-size: 13px;
}
</style>
