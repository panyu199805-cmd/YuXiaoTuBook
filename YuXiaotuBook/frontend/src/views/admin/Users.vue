<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { request } from '@/api/client'

const treeData = ref<any[]>([])
const total = ref(0)
const loadingTree = ref(false)
const loadingDetail = ref(false)
const selectedUserId = ref<number | null>(null)
const detail = ref<any>(null)
const editDialog = ref(false)
const editForm = ref({ nickname: '', province: '', city: '', status: 1 })

const defaultProps = { children: 'children', label: 'label' }

async function loadTree() {
  loadingTree.value = true
  try {
    const res = await request<any>({ url: '/admin/users/tree' })
    if (res.code === 200) {
      treeData.value = res.data.tree || []
      total.value = res.data.total || 0
    }
  } finally {
    loadingTree.value = false
  }
}

async function loadDetail(userId: number) {
  loadingDetail.value = true
  selectedUserId.value = userId
  try {
    const res = await request<any>({ url: `/admin/users/${userId}` })
    if (res.code === 200) detail.value = res.data
  } finally {
    loadingDetail.value = false
  }
}

function onNodeClick(node: any) {
  if (node.type === 'user' && node.user_id) loadDetail(node.user_id)
}

function openEdit() {
  if (!detail.value) return
  editForm.value = {
    nickname: detail.value.nickname,
    province: detail.value.province === '未填写' ? '' : detail.value.province,
    city: detail.value.city === '未填写' ? '' : detail.value.city,
    status: detail.value.status,
  }
  editDialog.value = true
}

async function saveEdit() {
  if (!selectedUserId.value) return
  const res = await request({
    url: `/admin/users/${selectedUserId.value}`,
    method: 'PUT',
    data: editForm.value,
  })
  if (res.code === 200) {
    editDialog.value = false
    detail.value = res.data
    loadTree()
  } else {
    alert(res.msg)
  }
}

onMounted(loadTree)
</script>

<template>
  <div class="page-card users-page">
    <div class="page-header">
      <h2>用户管理</h2>
      <span class="total">共 {{ total }} 位注册用户</span>
    </div>

    <div class="layout">
      <aside class="tree-panel">
        <p class="panel-title">按省份 / 城市</p>
        <el-tree
          v-loading="loadingTree"
          :data="treeData"
          :props="defaultProps"
          node-key="id"
          highlight-current
          default-expand-all
          @node-click="onNodeClick"
        />
      </aside>

      <main v-loading="loadingDetail" class="detail-panel">
        <template v-if="detail">
          <div class="detail-head">
            <div>
              <h3>{{ detail.nickname }}（{{ detail.username }}）</h3>
              <p class="meta">
                {{ detail.province }} · {{ detail.city }}
                · 注册 {{ detail.created_at?.slice(0, 10) }}
              </p>
            </div>
            <el-button size="small" @click="openEdit">编辑资料</el-button>
          </div>

          <el-row :gutter="16" class="stats">
            <el-col :span="8">
              <div class="stat-card">
                <span class="label">会员</span>
                <span class="value">{{ detail.member?.is_vip ? 'VIP' : '普通' }}</span>
                <span v-if="detail.member?.is_vip" class="sub">
                  至 {{ detail.member.expire_time?.slice(0, 10) }}
                </span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-card">
                <span class="label">收藏</span>
                <span class="value">{{ detail.stats?.favorite_count }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-card">
                <span class="label">图书订单</span>
                <span class="value">{{ detail.stats?.book_order_count }}</span>
              </div>
            </el-col>
          </el-row>

          <el-tabs>
            <el-tab-pane label="会员信息">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="是否 VIP">
                  {{ detail.member?.is_vip ? '是' : '否' }}
                </el-descriptions-item>
                <el-descriptions-item label="套餐">
                  {{ detail.member?.package_name || '—' }}
                </el-descriptions-item>
                <el-descriptions-item label="到期时间">
                  {{ detail.member?.expire_time?.slice(0, 19) || '—' }}
                </el-descriptions-item>
              </el-descriptions>
              <h4 v-if="detail.member_orders?.length" class="sub-title">会员订单</h4>
              <el-table v-if="detail.member_orders?.length" :data="detail.member_orders" size="small">
                <el-table-column prop="order_no" label="订单号" />
                <el-table-column prop="amount" label="金额" width="80" />
                <el-table-column prop="status" label="状态" width="100" />
                <el-table-column prop="pay_time" label="支付时间" min-width="160" />
              </el-table>
            </el-tab-pane>

            <el-tab-pane :label="`收藏（${detail.favorites?.length || 0}）`">
              <el-table :data="detail.favorites" size="small" empty-text="暂无收藏">
                <el-table-column prop="title" label="书名" />
                <el-table-column prop="author" label="作者" width="120" />
                <el-table-column label="分类" width="100">
                  <template #default="{ row }">{{ row.category?.name }}</template>
                </el-table-column>
                <el-table-column prop="collected_at" label="收藏时间" min-width="160" />
              </el-table>
            </el-tab-pane>

            <el-tab-pane :label="`图书订单（${detail.orders?.length || 0}）`">
              <el-table :data="detail.orders" size="small" empty-text="暂无订单" row-key="id">
                <el-table-column type="expand">
                  <template #default="{ row }">
                    <div class="expand-box">
                      <p><strong>收货人：</strong>{{ row.receiver_name }} {{ row.receiver_phone }}</p>
                      <p><strong>地址：</strong>{{ row.receiver_address }}</p>
                      <p v-if="row.ship_tracking_no">
                        <strong>物流：</strong>{{ row.ship_company }} {{ row.ship_tracking_no }}
                        <span v-if="row.shipped_at">（{{ row.shipped_at.slice(0, 10) }} 发货）</span>
                      </p>
                      <ul>
                        <li v-for="item in row.items" :key="item.book_id">
                          {{ item.book_title }} × {{ item.quantity }} · ¥{{ item.price }}
                        </li>
                      </ul>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="order_no" label="订单号" min-width="150" />
                <el-table-column prop="status_label" label="状态" width="90" />
                <el-table-column prop="total_amount" label="金额" width="80" />
                <el-table-column prop="pay_time" label="支付时间" min-width="160" />
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </template>
        <el-empty v-else description="请在左侧选择用户" />
      </main>
    </div>

    <el-dialog v-model="editDialog" title="编辑用户" width="420px">
      <el-form label-width="70px">
        <el-form-item label="昵称"><el-input v-model="editForm.nickname" /></el-form-item>
        <el-form-item label="省份"><el-input v-model="editForm.province" placeholder="如：浙江省" /></el-form-item>
        <el-form-item label="城市"><el-input v-model="editForm.city" placeholder="如：杭州市" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status">
            <el-option :value="1" label="正常" />
            <el-option :value="0" label="禁用" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialog = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.users-page { min-height: 520px; }
.total { color: #666; font-size: 14px; }
.layout { display: flex; gap: 16px; margin-top: 16px; min-height: 480px; }
.tree-panel {
  width: 280px; flex-shrink: 0; border: 1px solid #eee; border-radius: 8px; padding: 12px;
  background: #fafafa; overflow: auto;
}
.panel-title { font-size: 13px; color: #666; margin-bottom: 8px; }
.detail-panel { flex: 1; border: 1px solid #eee; border-radius: 8px; padding: 16px; background: #fff; }
.detail-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.detail-head h3 { margin: 0 0 6px; }
.meta { color: #666; font-size: 13px; margin: 0; }
.stats { margin-bottom: 16px; }
.stat-card {
  background: #f5f7fa; border-radius: 8px; padding: 12px 16px;
  display: flex; flex-direction: column; gap: 4px;
}
.stat-card .label { font-size: 12px; color: #666; }
.stat-card .value { font-size: 20px; font-weight: 600; color: #5d87ff; }
.stat-card .sub { font-size: 12px; color: #666; }
.sub-title { margin: 16px 0 8px; font-size: 14px; }
.expand-box { padding: 8px 16px; font-size: 13px; line-height: 1.8; }
.expand-box ul { margin: 8px 0 0; padding-left: 20px; }
</style>
