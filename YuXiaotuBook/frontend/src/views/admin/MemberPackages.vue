<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { request } from '@/api/client'

const packages = ref<any[]>([])
const dialog = ref(false)
const editingId = ref<number | null>(null)
const form = ref({
  package_name: '',
  price: 0,
  valid_day: 30,
  rights: '[]',
  status: 1,
})
const rightsText = ref('')

async function load() {
  const res = await request<any[]>({ url: '/admin/member/packages' })
  if (res.code === 200) packages.value = res.data
}

function openCreate() {
  editingId.value = null
  form.value = { package_name: '', price: 0, valid_day: 30, rights: '[]', status: 1 }
  rightsText.value = ''
  dialog.value = true
}

function openEdit(row: any) {
  editingId.value = row.id
  form.value = {
    package_name: row.package_name,
    price: row.price,
    valid_day: row.valid_day,
    rights: row.rights,
    status: row.status,
  }
  try {
    const parsed = JSON.parse(row.rights || '[]')
    rightsText.value = Array.isArray(parsed) ? parsed.join('\n') : row.rights
  } catch {
    rightsText.value = row.rights || ''
  }
  dialog.value = true
}

async function save() {
  const lines = rightsText.value.split('\n').map((s) => s.trim()).filter(Boolean)
  form.value.rights = JSON.stringify(lines)
  if (editingId.value) {
    await request({
      url: `/admin/member/packages/${editingId.value}`,
      method: 'PUT',
      data: form.value,
    })
  } else {
    await request({ url: '/admin/member/packages', method: 'POST', data: form.value })
  }
  dialog.value = false
  load()
}

async function remove(id: number) {
  if (!confirm('确定删除？')) return
  await request({ url: `/admin/member/packages/${id}`, method: 'DELETE' })
  load()
}

onMounted(load)
</script>

<template>
  <div class="page-card">
    <div class="page-header">
      <h2>会员套餐</h2>
      <el-button type="primary" @click="openCreate">+ 新增套餐</el-button>
    </div>
    <el-table :data="packages">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="package_name" label="套餐名" />
      <el-table-column prop="price" label="价格" width="100" />
      <el-table-column prop="valid_day" label="有效天数" width="100" />
      <el-table-column prop="status" label="状态" width="80" />
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialog" :title="editingId ? '编辑套餐' : '新增套餐'" width="480px">
      <el-form label-width="90px">
        <el-form-item label="套餐名"><el-input v-model="form.package_name" /></el-form-item>
        <el-form-item label="价格"><el-input-number v-model="form.price" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="有效天数"><el-input-number v-model="form.valid_day" :min="1" /></el-form-item>
        <el-form-item label="权益">
          <el-input v-model="rightsText" type="textarea" placeholder="每行一条权益" :rows="4" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option :value="1" label="上架" />
            <el-option :value="0" label="下架" />
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
