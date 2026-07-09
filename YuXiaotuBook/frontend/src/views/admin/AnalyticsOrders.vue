<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { fetchOrderStats, type OrderStats } from '@/api/adminStats'
import {
  buildBarRatios,
  buildTrendChart,
  formatMoney,
  formatNumber,
  formatShortDate,
  hourLabel,
} from '@/composables/useAnalyticsCharts'

const loading = ref(true)
const days = ref(30)
const data = ref<OrderStats | null>(null)

const statusBars = computed(() => buildBarRatios(
  (data.value?.status_stats || []).map((item) => ({ ...item, count: item.count })),
))
const orderTrend = computed(() => buildTrendChart(data.value?.order_trend || [], 'count', 720, 160))
const amountTrend = computed(() => buildTrendChart(data.value?.amount_trend || [], 'amount', 720, 160))
const hourChart = computed(() =>
  buildTrendChart(data.value?.hour_distribution || [], 'count', 360, 140),
)

async function loadData() {
  loading.value = true
  try {
    const res = await fetchOrderStats(days.value)
    if (res.code === 200) data.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
watch(days, loadData)
</script>

<template>
  <div v-loading="loading" class="analytics-page">
    <header class="page-hero">
      <div>
        <h1>交易订单数据统计</h1>
        <p>汇总图书订单与会员订单的数量、成交额、状态分布与热销榜单。</p>
      </div>
      <div class="toolbar-row">
        <el-radio-group v-model="days" size="small">
          <el-radio-button :value="7">近7天</el-radio-button>
          <el-radio-button :value="30">近30天</el-radio-button>
          <el-radio-button :value="90">近90天</el-radio-button>
        </el-radio-group>
      </div>
    </header>

    <div v-if="data" class="stat-grid">
      <div class="stat-card"><span>图书订单</span><strong>{{ formatNumber(data.summary.book_order_total) }}</strong></div>
      <div class="stat-card"><span>图书成交额</span><strong>¥{{ formatMoney(data.summary.book_revenue) }}</strong></div>
      <div class="stat-card"><span>会员订单</span><strong>{{ formatNumber(data.summary.member_order_total) }}</strong></div>
      <div class="stat-card"><span>会员成交额</span><strong>¥{{ formatMoney(data.summary.member_revenue) }}</strong></div>
    </div>

    <div class="panel-grid">
      <section class="panel-card">
        <div class="panel-header"><h3>订单量趋势</h3><p>近 {{ days }} 天每日新增图书订单</p></div>
        <svg class="trend-chart" :viewBox="`0 0 ${orderTrend.width} ${orderTrend.height}`" preserveAspectRatio="none">
          <path :d="orderTrend.area" fill="rgba(93,135,255,0.18)" />
          <polyline :points="orderTrend.line" fill="none" stroke="#5d87ff" stroke-width="2.2" />
        </svg>
        <div class="hour-axis">
          <span v-for="item in data?.order_trend.filter((_, i) => i % Math.ceil((data?.order_trend.length || 1) / 6) === 0) || []" :key="item.date">
            {{ formatShortDate(item.date) }}
          </span>
        </div>
      </section>

      <section class="panel-card">
        <div class="panel-header"><h3>成交额趋势</h3><p>已支付图书订单金额</p></div>
        <svg class="trend-chart" :viewBox="`0 0 ${amountTrend.width} ${amountTrend.height}`" preserveAspectRatio="none">
          <path :d="amountTrend.area" fill="rgba(247,127,0,0.16)" />
          <polyline :points="amountTrend.line" fill="none" stroke="#f77f00" stroke-width="2.2" />
        </svg>
      </section>

      <section class="panel-card">
        <div class="panel-header"><h3>订单状态分布</h3><p>当前全部图书订单状态</p></div>
        <div class="bar-list">
          <div v-for="item in statusBars" :key="item.status" class="bar-row">
            <span>{{ item.label }}</span>
            <div class="bar-track"><div class="bar-fill" :style="{ width: `${item.ratio}%` }" /></div>
            <em>{{ item.count }}</em>
          </div>
        </div>
      </section>

      <section class="panel-card">
        <div class="panel-header"><h3>下单时段分布</h3><p>按订单创建小时统计峰值</p></div>
        <svg class="trend-chart" :viewBox="`0 0 ${hourChart.width} ${hourChart.height}`" preserveAspectRatio="none">
          <path :d="hourChart.area" fill="rgba(45,106,79,0.16)" />
          <polyline :points="hourChart.line" fill="none" stroke="#2d6a4f" stroke-width="2.2" />
        </svg>
        <div class="hour-axis">
          <span v-for="item in data?.hour_distribution.filter((_, i) => i % 4 === 0) || []" :key="item.hour">
            {{ hourLabel(item.hour) }}
          </span>
        </div>
      </section>

      <section class="panel-card span-2">
        <div class="panel-header"><h3>热销图书 TOP</h3><p>按订单明细销量与销售额统计</p></div>
        <el-table :data="data?.top_sales || []" size="small">
          <el-table-column label="书籍" prop="title" min-width="200" />
          <el-table-column label="销量" prop="quantity" width="100" />
          <el-table-column label="销售额" width="120">
            <template #default="{ row }">¥{{ formatMoney(row.amount) }}</template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!data?.top_sales.length" description="暂无成交图书数据" :image-size="72" />
      </section>

      <section class="panel-card span-2">
        <div class="panel-header"><h3>近7日会员订单</h3><p>会员充值/续费订单趋势</p></div>
        <el-table :data="data?.member_trend || []" size="small">
          <el-table-column label="日期" width="120">
            <template #default="{ row }">{{ formatShortDate(row.date) }}</template>
          </el-table-column>
          <el-table-column label="订单数" prop="count" width="100" />
          <el-table-column label="成交额">
            <template #default="{ row }">¥{{ formatMoney(row.amount) }}</template>
          </el-table-column>
        </el-table>
      </section>
    </div>
  </div>
</template>

<style scoped>
@import './analytics-shared.css';

.page-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.page-hero .toolbar-row {
  margin-bottom: 0;
}
</style>
