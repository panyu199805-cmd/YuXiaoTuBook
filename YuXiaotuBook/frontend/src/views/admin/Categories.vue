<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { request } from '@/api/client'

const categories = ref<any[]>([])
const form = ref({ name: '', slug: '', sort_order: 0 })

async function load() {
  const res = await request<any[]>({ url: '/admin/categories' })
  if (res.code === 200) categories.value = res.data
}

async function add() {
  await request({ url: '/admin/categories', method: 'POST', data: form.value })
  form.value = { name: '', slug: '', sort_order: 0 }
  load()
}

async function remove(id: number) {
  await request({ url: `/admin/categories/${id}`, method: 'DELETE' })
  load()
}

onMounted(load)
</script>

<template>
  <div class="page-card">
    <div class="page-header">
      <h2>分类管理</h2>
    </div>
    <el-form inline style="margin-bottom: 16px">
      <el-input v-model="form.name" placeholder="名称" style="width: 120px" />
      <el-input v-model="form.slug" placeholder="slug" style="width: 120px" />
      <el-input-number v-model="form.sort_order" :min="0" />
      <el-button type="primary" @click="add">+ 添加</el-button>
    </el-form>
    <el-table :data="categories">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="slug" label="Slug" />
      <el-table-column prop="sort_order" label="排序" width="80" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>
