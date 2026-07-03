<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { request } from '@/api/client'

const items = ref<any[]>([])
const books = ref<any[]>([])
const dialog = ref(false)
const editingId = ref<number | null>(null)
const form = ref({
  book_id: 0,
  daily_sentence: '',
  daily_intro: '',
  publish_date: '',
  is_top: false,
  status: 1,
})

async function load() {
  const [d, b] = await Promise.all([
    request<any[]>({ url: '/admin/daily' }),
    request<any[]>({ url: '/admin/books' }),
  ])
  if (d.code === 200) items.value = d.data
  if (b.code === 200) {
    books.value = b.data
    if (!form.value.book_id && b.data.length) form.value.book_id = b.data[0].id
  }
}

function openCreate() {
  editingId.value = null
  form.value = {
    book_id: books.value[0]?.id || 0,
    daily_sentence: '',
    daily_intro: '',
    publish_date: new Date().toISOString().slice(0, 10),
    is_top: false,
    status: 1,
  }
  dialog.value = true
}

function openEdit(row: any) {
  editingId.value = row.id
  form.value = {
    book_id: row.book_id,
    daily_sentence: row.daily_sentence,
    daily_intro: row.daily_intro || '',
    publish_date: row.publish_date,
    is_top: row.is_top,
    status: row.status ?? 1,
  }
  dialog.value = true
}

async function save() {
  if (editingId.value) {
    await request({
      url: `/admin/daily/${editingId.value}`,
      method: 'PUT',
      data: form.value,
    })
  } else {
    await request({ url: '/admin/daily', method: 'POST', data: form.value })
  }
  dialog.value = false
  load()
}

async function remove(id: number) {
  if (!confirm('确定删除？')) return
  await request({ url: `/admin/daily/${id}`, method: 'DELETE' })
  load()
}

onMounted(load)
</script>

<template>
  <div class="page-card">
    <div class="page-header">
      <h2>每日读书</h2>
      <el-button type="primary" @click="openCreate">+ 新增内容</el-button>
    </div>
    <el-table :data="items">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="publish_date" label="日期" width="120" />
      <el-table-column prop="daily_sentence" label="金句" show-overflow-tooltip />
      <el-table-column label="书籍" width="160">
        <template #default="{ row }">{{ row.book?.title || row.book_id }}</template>
      </el-table-column>
      <el-table-column prop="like_count" label="点赞" width="80" />
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialog" :title="editingId ? '编辑每日读书' : '新增每日读书'" width="520px">
      <el-form label-width="80px">
        <el-form-item label="书籍">
          <el-select v-model="form.book_id" filterable>
            <el-option v-for="b in books" :key="b.id" :label="b.title" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="发布日期">
          <el-date-picker v-model="form.publish_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="金句"><el-input v-model="form.daily_sentence" type="textarea" /></el-form-item>
        <el-form-item label="简介"><el-input v-model="form.daily_intro" type="textarea" /></el-form-item>
        <el-form-item label="置顶"><el-switch v-model="form.is_top" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option :value="1" label="已发布" />
            <el-option :value="0" label="草稿" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
