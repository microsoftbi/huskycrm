<template>
  <div class="profile-page" v-loading="loading">
    <div class="page-header">
      <h2 class="page-title">个人信息</h2>
      <el-button type="primary" :loading="savingProfile" @click="handleSaveProfile">保存修改</el-button>
    </div>

    <!-- 基本信息 -->
    <el-card shadow="hover" class="profile-card">
      <template #header>
        <span class="card-title">基本信息</span>
      </template>
      <el-form :model="profileForm" label-position="top" class="profile-form">
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="用户名">
              <el-input v-model="profileForm.username" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="显示名称">
              <el-input v-model="profileForm.display_name" placeholder="请输入显示名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="邮箱">
              <el-input v-model="profileForm.email" placeholder="请输入邮箱地址" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="账户状态">
              <el-tag :type="profileForm.is_active ? 'success' : 'danger'" size="small">
                {{ profileForm.is_active ? '活跃' : '已停用' }}
              </el-tag>
              <el-tag v-if="profileForm.is_superuser" type="warning" size="small" style="margin-left:8px">管理员</el-tag>
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider />
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="创建时间">
              <span class="text-muted">{{ profileForm.created_at }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="上次更新">
              <span class="text-muted">{{ profileForm.updated_at }}</span>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 所属区域 -->
    <el-card shadow="hover" class="profile-card">
      <template #header>
        <span class="card-title">所属区域</span>
      </template>
      <el-table v-if="territories.length > 0" :data="territories" border size="small" style="width:100%">
        <el-table-column label="区域名称" min-width="180">
          <template #default="{ row }">
            <el-link type="primary" @click="goToTerritory(row.territory_id)">
              {{ row.territory_name }}
            </el-link>
            <span v-if="row.territory_code" class="text-muted" style="margin-left:6px">({{ row.territory_code }})</span>
          </template>
        </el-table-column>
        <el-table-column label="角色" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="row.role === 'manager' ? 'warning' : 'info'" size="small">
              {{ row.role === 'manager' ? '负责人' : '成员' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="负责人" min-width="150">
          <template #default="{ row }">
            <span v-if="row.manager_name">{{ row.manager_name }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="暂无区域归属" :image-size="80" />
    </el-card>

    <!-- 修改密码 -->
    <el-card shadow="hover" class="profile-card">
      <template #header>
        <span class="card-title">修改密码</span>
      </template>
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-position="top" class="profile-form">
        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item label="当前密码" prop="current_password">
              <el-input v-model="passwordForm.current_password" type="password" show-password placeholder="输入当前密码" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="passwordForm.new_password" type="password" show-password placeholder="至少6位" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="确认密码" prop="confirm_password">
              <el-input v-model="passwordForm.confirm_password" type="password" show-password placeholder="再次输入新密码" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" :loading="savingPassword" @click="handleChangePassword">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../../stores/authStore'
import { authApi } from '../../api/auth'
import { profileApi, type UserTerritory } from '../../api/profile'

const router = useRouter()
const auth = useAuthStore()

const loading = ref(false)
const savingProfile = ref(false)
const savingPassword = ref(false)
const passwordFormRef = ref<any>(null)
const territories = ref<UserTerritory[]>([])

const profileForm = reactive({
  username: '',
  display_name: '',
  email: '',
  is_active: false,
  is_superuser: false,
  created_at: '',
  updated_at: '',
})

const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: '',
})

const passwordRules = {
  current_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (_rule: any, value: string, callback: any) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  })
}

async function fetchProfile() {
  loading.value = true
  try {
    const { data } = await authApi.me()
    profileForm.username = data.username
    profileForm.display_name = data.display_name || ''
    profileForm.email = data.email
    profileForm.is_active = data.is_active
    profileForm.is_superuser = data.is_superuser
    profileForm.created_at = formatDate(data.created_at)
    profileForm.updated_at = formatDate(data.updated_at)
    // Sync to auth store
    auth.user = data as any
  } catch {
    ElMessage.error('加载用户信息失败')
  } finally {
    loading.value = false
  }
}

async function fetchTerritories() {
  try {
    const { data } = await profileApi.getMyTerritories()
    territories.value = data
  } catch {
    // Non-critical
  }
}

async function handleSaveProfile() {
  savingProfile.value = true
  try {
    await profileApi.updateProfile({
      display_name: profileForm.display_name || undefined,
      email: profileForm.email || undefined,
    })
    ElMessage.success('保存成功')
    // Refresh user data
    await auth.fetchUser()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  } finally {
    savingProfile.value = false
  }
}

async function handleChangePassword() {
  const valid = await passwordFormRef.value?.validate().catch(() => false)
  if (!valid) return

  savingPassword.value = true
  try {
    await profileApi.changePassword({
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password,
      confirm_password: passwordForm.confirm_password,
    })
    ElMessage.success('密码修改成功')
    passwordForm.current_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '密码修改失败')
  } finally {
    savingPassword.value = false
  }
}

function goToTerritory(id: string) {
  router.push(`/admin/territories`)
}

onMounted(async () => {
  await fetchProfile()
  await fetchTerritories()
})
</script>

<style scoped>
.profile-page {
  max-width: 960px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
  font-size: 22px;
  color: #333;
}

.profile-card {
  margin-bottom: 20px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.profile-form {
  max-width: 100%;
}

.text-muted {
  color: #999;
  font-size: 13px;
}
</style>
