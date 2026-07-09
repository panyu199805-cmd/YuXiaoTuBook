<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { fetchReadingStats, type ReadingStats } from '@/api/adminStats'
import {
  buildBarRatios,
  buildTrendChart,
  formatNumber,
  formatShortDate,
  hourLabel,
} from '@/composables/useAnalyticsCharts'
import { placeholderCover, resolveMediaUrl } from '@/utils/media'

const loading = ref(true)
const data = ref<ReadingStats | null>(null)

const preferenceBars = computed(() => buildBarRatios(data.value?.preference_stats || []))
const hourChart = computed(() =>
  buildTrendChart(
    (data.value?.hour_distribution || []).map((item) => ({ hour: item.hour, count: item.count })),
    'count',
    720,
    160,
  ),
)

onMounted(async () => {
  loading.value = true
  try {
    const res = await fetchReadingStats()
    if (res.code === 200) data.value = res.data
  } finally {
    loading.value = false
  }
})

function cover(url: string, id: number) {
  return resolveMediaUrl(url, id)
}
</script>

<template>
  <div v-loading="loading" class="analytics-page">
    <header class="page-hero">
      <div>
        <h1>用户阅读行为分析</h1>
        <p>基于浏览量、播放、收藏、浏览记录与用户喜好分类的真实数据统计。</p>
      </div>
    </header>

    <div v-if="data" class="stat-grid">
      <div class="stat-card"><span>总浏览量</span><strong>{{ formatNumber(data.summary.total_views) }}</strong></div>
      <div class="stat-card"><span>总播放量</span><strong>{{ formatNumber(data.summary.total_plays) }}</strong></div>
      <div class="stat-card"><span>收藏次数</span><strong>{{ formatNumber(data.summary.favorite_total) }}</strong></div>
      <div class="stat-card"><span>浏览记录</span><strong>{{ formatNumber(data.summary.history_total) }}</strong></div>
    </div>

    <div class="panel-grid">
      <section class="panel-card span-2">
        <div class="panel-header"><h3>书籍内容消费排行</h3><p>按浏览量排序，附带播放、收藏与浏览记录</p></div>
        <el-table :data="data?.video_ranking || []" size="small">
          <el-table-column label="书籍" min-width="180">
            <template #default="{ row }">
              <div class="book-cell">
                <img :src="cover(row.cover, row.id)" :alt="row.title" @error="($event.target as HTMLImageElement).src = placeholderCover(row.id)" />
                <span>{{ row.title }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="浏览" prop="view_count" width="80" />
          <el-table-column label="播放" prop="play_count" width="80" />
          <el-table-column label="收藏" prop="favorite_count" width="80" />
          <el-table-column label="浏览记录" prop="history_count" width="90" />
        </el-table>
      </section>

      <section class="panel-card">
        <div class="panel-header"><h3>用户偏好分类</h3><p>来自个人中心读书喜好设置</p></div>
        <div v-if="preferenceBars.length" class="bar-list">
          <div v-for="item in preferenceBars" :key="item.name" class="bar-row">
            <span>{{ item.name }}</span>
            <div class="bar-track"><div class="bar-fill" :style="{ width: `${item.ratio}%` }" /></div>
            <em>{{ item.count }}</em>
          </div>
        </div>
        <el-empty v-else description="暂无用户喜好数据" :image-size="72" />
      </section>

      <section class="panel-card">
        <div class="panel-header"><h3>活跃时段分布</h3><p>按浏览/收藏记录发生小时统计</p></div>
        <svg class="trend-chart" :viewBox="`0 0 ${hourChart.width} ${hourChart.height}`" preserveAspectRatio="none">
          <path :d="hourChart.area" fill="rgba(93,135,255,0.18)" />
          <polyline :points="hourChart.line" fill="none" stroke="#5d87ff" stroke-width="2.2" />
        </svg>
        <div class="hour-axis">
          <span v-for="item in data?.hour_distribution.filter((_, i) => i % 4 === 0) || []" :key="item.hour">
            {{ hourLabel(item.hour) }}
          </span>
        </div>
      </section>

      <section class="panel-card span-2">
        <div class="panel-header"><h3>每日读书专栏表现</h3><p>最近发布的专栏内容与点赞数</p></div>
        <el-table :data="data?.daily_stats || []" size="small">
          <el-table-column label="期数内容" prop="title" min-width="180" />
          <el-table-column label="发布日期" width="120">
            <template #default="{ row }">{{ formatShortDate(row.publish_date) }}</template>
          </el-table-column>
          <el-table-column label="点赞" prop="like_count" width="80" />
          <el-table-column label="置顶" width="80">
            <template #default="{ row }">
              <el-tag v-if="row.is_top" size="small" type="warning">置顶</el-tag>
              <span v-else>—</span>
            </template>
          </el-table-column>
        </el-table>
      </section>
    </div>
  </div>
</template>

<style scoped>
@import './analytics-shared.css';
</style>
