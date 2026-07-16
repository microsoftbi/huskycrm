<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <el-icon :size="40" color="#409eff"><aim /></el-icon>
        <h2>Husky CRM</h2>
        <p class="login-subtitle">登录到您的账户</p>
      </div>

      <el-tabs v-model="activeTab" class="login-tabs">
        <el-tab-pane label="登录" name="login">
          <el-form ref="loginForm" :model="loginData" :rules="loginRules" label-position="top">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="loginData.username" placeholder="请输入用户名" />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input v-model="loginData.password" type="password" show-password placeholder="请输入密码" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="auth.loading" class="login-btn" @click="handleLogin">
                登录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="注册" name="register">
          <el-form ref="registerForm" :model="registerData" :rules="registerRules" label-position="top">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="registerData.username" placeholder="请输入用户名" />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="registerData.email" placeholder="请输入邮箱" />
            </el-form-item>
            <el-form-item label="显示名称">
              <el-input v-model="registerData.displayName" placeholder="可选" />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input v-model="registerData.password" type="password" show-password placeholder="请输入密码" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="auth.loading" class="login-btn" @click="handleRegister">
                注册
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/authStore'

const router = useRouter()
const auth = useAuthStore()

const activeTab = ref('login')
const loginForm = ref()
const registerForm = ref()

const loginData = reactive({ username: '', password: '' })
const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const registerData = reactive({ username: '', email: '', password: '', displayName: '' })
const registerRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  if (!loginForm.value) return
  const valid = await loginForm.value.validate().catch(() => false)
  if (!valid) return

  try {
    await auth.login(loginData.username, loginData.password)
    ElMessage.success('登录成功')
    router.push('/')
  } catch {
    ElMessage.error('用户名或密码错误')
  }
}

async function handleRegister() {
  if (!registerForm.value) return
  const valid = await registerForm.value.validate().catch(() => false)
  if (!valid) return

  try {
    const success = await auth.register(
      registerData.username,
      registerData.email,
      registerData.password,
      registerData.displayName || undefined
    )
    if (success) {
      ElMessage.success('注册成功')
      router.push('/')
    }
  } catch {
    ElMessage.error('注册失败，用户名或邮箱可能已存在')
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 420px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  margin: 12px 0 4px;
  font-size: 24px;
  color: #333;
}

.login-subtitle {
  color: #999;
  font-size: 14px;
  margin: 0;
}

.login-tabs {
  margin-bottom: 20px;
}

.login-btn {
  width: 100%;
}
</style>
