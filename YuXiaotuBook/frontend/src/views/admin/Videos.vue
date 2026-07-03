<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { request } from '@/api/client'

const videos = ref<any[]>([])
const dialog = ref(false)
const editingId = ref<number | null>(null)
const form = ref({
  book_id: 1,
  video_cover: '',
  video_url: '',
  video_duration: 360,
  video_intro: '',
  status: 1,
})

function openCreate() {
  editingId.value = null
  form.value = {
    book_id: 1,
    video_cover: '',
    video_url: '',
    video_duration: 360,
    video_intro: '',
    status: 1,
  }
  dialog.value = true
}

function openEdit(row: any) {
  editingId.value = row.id
  form.value = {
    book_id: row.book_id,
    video_cover: row.video_cover || '',
    video_url: row.video_url || '',
    video_duration: row.video_duration ?? 360,
    video_intro: row.video_intro || '',
    status: row.status ?? 1,
  }
  dialog.value = true
}

async function load() {
  const res = await request<any[]>({ url: '/admin/videos' })
  if (res.code === 200) videos.value = res.data
}

async function save() {
  const res = await request({ url: '/admin/videos', method: 'POST', data: form.value })
  if (res.code === 200) {
    dialog.value = false
    load()
  } else {
    alert(res.msg)
  }
}

async function remove(id: number) {
  if (!confirm('确定删除该视频绑定？删除后对应书籍将无法播放解读视频。')) return
  const res = await request({ url: `/admin/videos/${id}`, method: 'DELETE' })
  if (res.code === 200) {
    load()
  } else {
    alert(res.msg)
  }
}

onMounted(load)
</script>

<template>
  <div class="page-card">
    <div class="page-header">
      <h2>视频管理</h2>
      <el-button type="primary" @click="openCreate">+ 绑定视频</el-button>
    </div>
    <el-table :data="videos">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="book_id" label="书籍ID" width="80" />
      <el-table-column prop="video_url" label="视频URL" show-overflow-tooltip />
      <el-table-column prop="play_count" label="播放量" width="80" />
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{ row }">{{ row.status === 1 ? '上架' : '下架' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialog" :title="editingId ? '编辑视频' : '绑定视频'" width="500px">
      <el-form label-width="100px">
        <el-form-item label="书籍ID">
          <el-input-number v-model="form.book_id" :min="1" :disabled="!!editingId" />
        </el-form-item>
        <el-form-item label="封面URL"><el-input v-model="form.video_cover" /></el-form-item>
        <el-form-item label="视频URL"><el-input v-model="form.video_url" /></el-form-item>
        <el-form-item label="时长(秒)"><el-input-number v-model="form.video_duration" :min="0" /></el-form-item>
        <el-form-item label="简介"><el-input v-model="form.video_intro" type="textarea" /></el-form-item>
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
