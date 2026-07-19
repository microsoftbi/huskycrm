<template>
  <div class="profile-management" v-loading="loading">
    <div class="pm-header">
      <h3 class="pm-title">Profile管理</h3>
      <el-button type="primary" size="small" @click="handleCreate">新建Profile</el-button>
    </div>

    <div class="pm-layout">
      <!-- Left: Profile list -->
      <div class="pm-list">
        <div
          v-for="p in profiles"
          :key="p.id"
          class="pm-list-item"
          :class="{ active: selectedId === p.id }"
          @click="selectProfile(p.id)"
        >
          <div class="pm-list-item-name">{{ p.name }}</div>
          <div class="pm-list-item-type">{{ typeLabel(p.profile_type) }}</div>
          <div class="pm-list-item-count">{{ p.user_count }} 用户</div>
        </div>
      </div>

      <!-- Right: Profile detail -->
      <div class="pm-detail" v-if="selectedProfile">
        <el-form :model="editForm" label-position="top">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="名称">
                <el-input v-model="editForm.name" :disabled="selectedProfile.is_system" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="类型">
                <el-select v-model="editForm.profile_type" :disabled="selectedProfile.is_system" style="width:100%">
                  <el-option label="管理员" value="admin" />
                  <el-option label="标准用户" value="standard" />
                  <el-option label="只读用户" value="readonly" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="描述">
            <el-input v-model="editForm.description" type="textarea" :rows="2" />
          </el-form-item>
        </el-form>

        <!-- Permission Summary -->
        <el-divider />
        <h4 class="pm-section-title">权限摘要</h4>
        <el-table :data="permissionSummary" border size="small" style="width:100%">
          <el-table-column label="操作" prop="action" width="120" />
          <el-table-column label="权限" width="100" align="center">
            <template #default="{ row }">
              <el-icon v-if="row.granted" color="#67c23a"><check /></el-icon>
              <el-icon v-else color="#f56c6c"><close /></el-icon>
            </template>
          </el-table-column>
          <el-table-column label="说明" prop="note" />
        </el-table>

        <!-- Users assigned to this profile -->
        <el-divider />
        <h4 class="pm-section-title">所属用户 ({{ selectedProfile.user_count }})</h4>
        <el-table :data="selectedProfile.users" border size="small" style="width:100%" v-if="selectedProfile.users.length > 0">
          <el-table-column label="用户名" prop="username" width="150" />
          <el-table-column label="显示名称" width="150">
            <template #default="{ row }">
              {{ row.display_name || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="邮箱" prop="email" min-width="200" />
          <el-table-column label="状态" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
                {{ row.is_active ? '活跃' : '停用' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂无用户分配此Profile" :image-size="60" />

        <el-divider />
        <div class="pm-actions">
          <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
          <el-button
            v-if="!selectedProfile.is_system"
            type="danger"
            plain
            :loading="deleting"
            @click="handleDelete"
          >删除</el-button>
        </div>
      </div>
      <el-empty v-else description="请选择一个Profile" :image-size="80" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Close } from '@element-plus/icons-vue'
import { profilesApi } from '../../api/profiles'
import type { Profile } from '../../types/profile'

const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const profiles = ref<Profile[]>([])
const selectedId = ref<string | null>(null)
const selectedProfile = ref<Profile | null>(null)

const editForm = reactive({
  name: '',
  profile_type: 'standard',
  description: '',
})

const permissionSummary = computed(() => {
  const type = editForm.profile_type
  const rules: Record<string, { read: boolean; create: boolean; edit: boolean; delete: boolean }> = {
    admin: { read: true, create: true, edit: true, delete: true },
    standard: { read: true, create: true, edit: true, delete: false },
    readonly: { read: true, create: false, edit: false, delete: false },
  }
  const perms = rules[type] || rules.readonly
  return [
    { action: '查看数据', granted: perms.read, note: '浏览列表和详情' },
    { action: '创建记录', granted: perms.create, note: '新建账户、联系人、商机等' },
    { action: '编辑记录', granted: perms.edit, note: '修改已有数据' },
    { action: '删除记录', granted: perms.delete, note: '永久删除数据' },
  ]
})

function typeLabel(t: string): string {
  const map: Record<string, string> = { admin: '管理员', standard: '标准用户', readonly: '只读用户' }
  return map[t] || t
}

async function fetchProfiles() {
  loading.value = true
  try {
    const { data } = await profilesApi.list()
    profiles.value = data
  } catch {
    ElMessage.error('加载Profile列表失败')
  } finally {
    loading.value = false
  }
}

async function selectProfile(id: string) {
  selectedId.value = id
  try {
    const { data } = await profilesApi.get(id)
    selectedProfile.value = data
    editForm.name = data.name
    editForm.profile_type = data.profile_type
    editForm.description = data.description || ''
  } catch {
    ElMessage.error('加载Profile详情失败')
  }
}

async function handleSave() {
  if (!selectedId.value) return
  saving.value = true
  try {
    const { data } = await profilesApi.update(selectedId.value, {
      name: editForm.name || undefined,
      profile_type: editForm.profile_type,
      description: editForm.description || undefined,
    })
    ElMessage.success('保存成功')
    // Update local list
    const idx = profiles.value.findIndex(x => x.id === data.id)
    if (idx >= 0) profiles.value[idx] = data
    selectedProfile.value = data
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  if (!selectedId.value) return
  try {
    await ElMessageBox.confirm('确定删除此Profile？此操作不可撤销。', '确认删除', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
    deleting.value = true
    await profilesApi.delete(selectedId.value)
    ElMessage.success('已删除')
    selectedId.value = null
    selectedProfile.value = null
    await fetchProfiles()
  } catch (e: any) {
    if (e?.response?.data?.detail) {
      ElMessage.error(e.response.data.detail)
    }
  } finally {
    deleting.value = false
  }
}

async function handleCreate() {
  try {
    await ElMessageBox.prompt('请输入新Profile名称', '新建Profile', {
      inputPattern: /.+/,
      inputErrorMessage: '名称不能为空',
    })
    // TODO: open create dialog or simply create with default
    ElMessage.info('创建功能可通过 API 实现')
  } catch { /* cancelled */ }
}

onMounted(fetchProfiles)
</script>

<style scoped>
.profile-management {
  height: 100%;
}

.pm-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.pm-title {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.pm-layout {
  display: flex;
  gap: 20px;
  height: calc(100% - 50px);
}

.pm-list {
  width: 240px;
  min-width: 240px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow-y: auto;
}

.pm-list-item {
  padding: 12px 14px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.1s;
}

.pm-list-item:hover {
  background: #f4f6f9;
}

.pm-list-item.active {
  background: #e8f0fe;
  border-left: 3px solid #1589ee;
}

.pm-list-item-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.pm-list-item-type {
  font-size: 11px;
  color: #909399;
  margin-bottom: 2px;
}

.pm-list-item-count {
  font-size: 11px;
  color: #909399;
}

.pm-detail {
  flex: 1;
  overflow-y: auto;
}

.pm-section-title {
  margin: 0 0 12px;
  font-size: 14px;
  color: #333;
}

.pm-actions {
  display: flex;
  gap: 10px;
}
</style>