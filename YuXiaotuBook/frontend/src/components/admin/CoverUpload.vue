<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadRequestOptions } from 'element-plus'
import { uploadAdminFile } from '@/utils/adminUpload'

const model = defineModel<string>({ default: '' })

const uploading = ref(false)

const previewUrl = computed(() => model.value || '')

async function handleUpload(options: UploadRequestOptions) {
  uploading.value = true
  try {
    const data = await uploadAdminFile(options.file)
    model.value = data.url
    ElMessage.success('封面上传成功')
    options.onSuccess?.(data)
  } catch (err) {
    const message = err instanceof Error ? err.message : '上传失败，请稍后重试'
    ElMessage.error(message === 'upload failed' ? '上传失败，请稍后重试' : message)
    options.onError?.(new Error(message) as never)
  } finally {
    uploading.value = false
  }
}

function beforeUpload(file: File) {
  const allowed = ['image/jpeg', 'image/png', 'image/webp']
  if (!allowed.includes(file.type)) {
    ElMessage.warning('仅支持 JPG / PNG / WebP 格式')
    return false
  }
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.warning('图片大小不能超过 5MB')
    return false
  }
  return true
}

function removeCover() {
  model.value = ''
}
</script>

<template>
  <div class="cover-upload">
    <el-upload
      class="cover-uploader"
      :show-file-list="false"
      accept=".jpg,.jpeg,.png,.webp"
      :http-request="handleUpload"
      :before-upload="beforeUpload"
      :disabled="uploading"
    >
      <img v-if="previewUrl" :src="previewUrl" class="cover-preview" alt="封面预览" />
      <div v-else class="cover-placeholder">
        <span class="icon">+</span>
        <span class="text">{{ uploading ? '上传中…' : '点击选择本地图片' }}</span>
        <span class="hint">支持 JPG / PNG / WebP，最大 5MB</span>
      </div>
    </el-upload>
    <div v-if="previewUrl" class="cover-actions">
      <span class="cover-path">{{ model }}</span>
      <el-button link type="danger" @click="removeCover">移除封面</el-button>
    </div>
  </div>
</template>

<style scoped>
.cover-upload {
  width: 100%;
}

.cover-uploader :deep(.el-upload) {
  border: 1px dashed var(--el-border-color);
  border-radius: 8px;
  cursor: pointer;
  overflow: hidden;
  transition: border-color 0.2s;
}

.cover-uploader :deep(.el-upload:hover) {
  border-color: var(--el-color-primary);
}

.cover-preview {
  display: block;
  width: 140px;
  height: 186px;
  object-fit: cover;
}

.cover-placeholder {
  width: 140px;
  height: 186px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px;
  color: var(--el-text-color-secondary);
  background: var(--el-fill-color-light);
}

.cover-placeholder .icon {
  font-size: 28px;
  line-height: 1;
  color: var(--el-color-primary);
}

.cover-placeholder .text {
  font-size: 13px;
  text-align: center;
}

.cover-placeholder .hint {
  font-size: 11px;
  text-align: center;
  opacity: 0.75;
}

.cover-actions {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cover-path {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  word-break: break-all;
}
</style>
