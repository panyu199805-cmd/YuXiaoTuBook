<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import AuthBrandPanel from '@/components/admin/AuthBrandPanel.vue'
import { request } from '@/api/client'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const store = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const form = reactive({ username: 'admin', password: '' })

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function submit() {
  await formRef.value?.validate()
  loading.value = true
  try {
    const res = await request<any>({
      url: '/auth/login',
      method: 'POST',
      data: form,
    })
    if (res.code === 200 && res.data.user.role === 'admin') {
      store.setAuth(res.data.token, res.data.user)
      router.push('/admin/books')
      return
    }
    ElMessage.error(res.code === 200 ? '非管理员账号' : res.msg)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <AuthBrandPanel />

    <div class="auth-form-side">
      <div class="auth-card">
        <div class="auth-logo">
          <div class="logo-icon">宇</div>
          <span class="logo-text">宇小兔 · 管理后台</span>
        </div>
        <h2>欢迎回来</h2>
        <p class="subtitle">请登录您的管理账号</p>
        <el-form ref="formRef" :model="form" :rules="rules" size="large" @submit.prevent="submit">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="密码"
              prefix-icon="Lock"
              show-password
              @keyup.enter="submit"
            />
          </el-form-item>
          <el-button type="primary" class="submit-btn" :loading="loading" @click="submit">登 录</el-button>
        </el-form>
        <p class="hint">默认账号 admin / admin123456</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  background: #fff;
}

.auth-form-side {
  width: 480px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  padding: 40px;
  flex-shrink: 0;
}

.auth-card {
  width: 100%;
  max-width: 360px;
}

.auth-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 28px;
}

.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--ecms-primary, #5d87ff), #7c3aed);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 18px;
}

.logo-text {
  font-size: 16px;
  font-weight: 700;
  color: #1d2129;
}

h2 {
  font-size: 26px;
  font-weight: 700;
  color: #1d2129;
  margin: 0 0 6px;
}

.subtitle {
  color: #86909c;
  margin: 0 0 32px;
}

.submit-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  margin-top: 8px;
}

.hint {
  margin-top: 16px;
  font-size: 12px;
  color: #86909c;
  text-align: center;
}

@media (max-width: 768px) {
  .auth-form-side {
    width: 100%;
  }
}
</style>
