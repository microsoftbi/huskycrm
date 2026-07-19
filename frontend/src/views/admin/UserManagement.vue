<template>
  <div class="user-management" v-loading="loading">
    <div class="um-header">
      <h3 class="um-title">用户管理</h3>
      <el-button type="primary" size="small" @click="showCreateDialog = true">新建用户</el-button>
    </div>

    <el-table :data="users" border stripe size="small" style="width:100%">
      <el-table-column label="用户名" prop="username" min-width="120" />
      <el-table-column label="显示名称" prop="display_name" min-width="120">
        <template #default="{ row }">
          <span v-if="editingId === row.id">
            <el-input v-model="editForm.display_name" size="small" style="width:120px" />
          </span>
          <span v-else>{{ row.display_name || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="邮箱" prop="email" min-width="180">
        <template #default="{ row }">
          <span v-if="editingId === row.id">
            <el-input v-model="editForm.email" size="small" style="width:180px" />
          </span>
          <span v-else>{{ row.email }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Profile" min-width="140">
        <template #default="{ row }">
          <span v-if="editingId === row.id">
            <el-select v-model="editForm.profile_id" placeholder="选择Profile" size="small" style="width:140px" clearable>
              <el-option v-for="p in profiles" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
          </span>
          <span v-else>
            <el-tag size="small">{{ row.profile_name || '-' }}</el-tag>
          </span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag v-if="editingId === row.id">
            <el-switch v-model="editForm.is_active" size="small" />
          </el-tag>
          <el-tag v-else :type="row.is_active ? 'success' : 'danger'" size="small">
            {{ row.is_active ? '活跃' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="管理员" width="70" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.is_superuser" type="warning" size="small">是</el-tag>
          <span v-else class="text-muted">否</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="130" align="center" fixed="right">
        <template #default="{ row }">
          <template v-if="editingId === row.id">
            <el-button type="primary" link size="small" @click="handleSave(row.id)">保存</el-button>
            <el-button link size="small" @click="cancelEdit">取消</el-button>
          </template>
          <template v-else>
            <el-button type="primary" link size="small" @click="startEdit(row)">编辑</el-button>
          </template>
        </template>
      </el-table-column>
    </el-table>

    <!-- Create User Dialog -->
    <el-dialog v-model="showCreateDialog" title="新建用户" width="420px">
      <el-form :model="createForm" label-position="top">
        <el-form-item label="用户名" required>
          <el-input v-model="createForm.username" placeholder="登录用户名" />
        </el-form-item>
        <el-form-item label="邮箱" required>
          <el-input v-model="createForm.email" placeholder="邮箱地址" />
        </el-form-item>
        <el-form-item label="密码" required>
          <el-input v-model="createForm.password" type="password" show-password placeholder="至少6位" />
        </el-form-item>
        <el-form-item label="显示名称">
          <el-input v-model="createForm.display_name" placeholder="显示名称" />
        </el-form-item>
        <el-form-item label="Profile">
          <el-select v-model="createForm.profile_id" placeholder="选择Profile" style="width:100%" clearable>
            <el-option v-for="p in profiles" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="管理员">
          <el-switch v-model="createForm.is_superuser" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { authApi } from '../../api/auth'
import { profilesApi } from '../../api/profiles'
import type { User } from '../../types/auth'
import type { ProfileBrief } from '../../types/profile'

const loading = ref(false)
const creating = ref(false)
const users = ref<User[]>([])
const profiles = ref<ProfileBrief[]>([])
const showCreateDialog = ref(false)
const editingId = ref<string | null>(null)
const editForm = ref({ display_name: '', email: '', is_active: true, profile_id: '' })
const createForm = ref({
  username: '', email: '', password: '', display_name: '', is_superuser: false, profile_id: '',
})

async function fetchUsers() {
  loading.value = true
  try {
    const { data } = await authApi.listUsers()
    users.value = data
  } catch {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchProfiles() {
  try {
    const { data } = await profilesApi.brief()
    profiles.value = data
  } catch { /* optional */ }
}

function startEdit(user: User) {
  editingId.value = user.id
  editForm.value = {
    display_name: user.display_name || '',
    email: user.email,
    is_active: user.is_active,
    profile_id: user.profile_id || '',
  }
}

function cancelEdit() {
  editingId.value = null
}

async function handleSave(userId: string) {
  try {
    await authApi.updateUser(userId, {
      display_name: editForm.value.display_name || undefined,
      email: editForm.value.email || undefined,
      is_active: editForm.value.is_active,
      profile_id: editForm.value.profile_id || undefined,
    })
    ElMessage.success('更新成功')
    editingId.value = null
    await fetchUsers()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '更新失败')
  }
}

async function handleCreate() {
  if (!createForm.value.username || !createForm.value.email || !createForm.value.password) {
    ElMessage.warning('请填写必填字段')
    return
  }
  if (createForm.value.password.length < 6) {
    ElMessage.warning('密码至少6位')
    return
  }
  creating.value = true
  try {
    await authApi.register({
      username: createForm.value.username,
      email: createForm.value.email,
      password: createForm.value.password,
      display_name: createForm.value.display_name || undefined,
    })
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    createForm.value = { username: '', email: '', password: '', display_name: '', is_superuser: false, profile_id: '' }
    await fetchUsers()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '创建失败')
  } finally {
    creating.value = false
  }
}

onMounted(() => {
  fetchUsers()
  fetchProfiles()
})
</script>

<style scoped>
.user-management {
  height: 100%;
}

.um-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.um-title {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.text-muted {
  color: #999;
  font-size: 12px;
}
</style>