import http from '@/api/client'

export interface AdminUploadResult {
  url: string
  media_type?: string
}

/** 管理后台统一文件上传（POST /admin/upload） */
export async function uploadAdminFile(file: File): Promise<AdminUploadResult> {
  const formData = new FormData()
  formData.append('file', file)
  const res = await http.post('/admin/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  const body = res.data
  if (body.code === 200 && body.data?.url) {
    return body.data as AdminUploadResult
  }
  throw new Error(body.msg || 'upload failed')
}
