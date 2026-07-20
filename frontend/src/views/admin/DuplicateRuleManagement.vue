<template>
  <div class="duplicate-rule-page">
    <div class="page-header">
      <h3>重复检测规则</h3>
      <el-button size="small" type="primary" @click="openCreate">新建规则</el-button>
    </div>

    <el-table :data="items" v-loading="loading" stripe style="width: 100%">
      <el-table-column prop="name" label="规则名称" min-width="160" />
      <el-table-column prop="object_type" label="对象" width="120">
        <template #default="{ row }">
          {{ typeLabel(row.object_type) }}
        </template>
      </el-table-column>
      <el-table-column prop="matching_fields" label="匹配字段" min-width="200">
        <template #default="{ row }">
          <el-tag
            v-for="f in parseFields(row.matching_fields)"
            :key="f"
            size="small"
            style="margin-right: 4px"
          >
            {{ fieldLabel(row.object_type, f) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="warning" link @click="toggleActive(row)">
            {{ row.is_active ? '禁用' : '启用' }}
          </el-button>
          <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        small
        @current-change="loadData"
      />
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialog.visible"
      :title="dialog.isEdit ? '编辑重复检测规则' : '新建重复检测规则'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" label-width="100px" size="small">
        <el-form-item label="规则名称" required>
          <el-input v-model="form.name" placeholder="如：账户名称重复检测" />
        </el-form-item>
        <el-form-item label="对象" required>
          <el-select v-model="form.object_type" style="width: 100%">
            <el-option label="账户" value="account" />
            <el-option label="联系人" value="contact" />
          </el-select>
        </el-form-item>
        <el-form-item label="匹配字段" required>
          <el-checkbox-group v-model="selectedFields">
            <el-checkbox
              v-for="f in availableFields"
              :key="f.value"
              :label="f.value"
              :disabled="dialog.isEdit"
            >
              {{ f.label }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button size="small" @click="dialog.visible = false">取消</el-button>
        <el-button size="small" type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface DuplicateRule {
  id: string
  name: string
  object_type: string
  is_active: boolean
  matching_fields: string
  created_at: string
  updated_at: string
}

const FIELD_OPTIONS: Record<string, { label: string; value: string }[]> = {
  account: [
    { label: '名称', value: 'name' },
    { label: '邮箱', value: 'email' },
    { label: '电话', value: 'phone' },
    { label: '网站', value: 'website' },
  ],
  contact: [
    { label: '邮箱', value: 'email' },
    { label: '电话', value: 'phone' },
    { label: '手机', value: 'mobile_phone' },
  ],
}

const loading = ref(false)
const items = ref<DuplicateRule[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const dialog = reactive({
  visible: false,
  isEdit: false,
  editId: '',
})

const form = reactive({
  name: '',
  object_type: 'account',
  is_active: true,
  matching_fields: '[]',
})

const selectedFields = ref<string[]>([])

const availableFields = ref(FIELD_OPTIONS.account)

watch(() => form.object_type, (val) => {
  availableFields.value = FIELD_OPTIONS[val] || []
})

function typeLabel(type: string): string {
  const labels: Record<string, string> = { account: '账户', contact: '联系人' }
  return labels[type] || type
}

function fieldLabel(objType: string, field: string): string {
  const opts = FIELD_OPTIONS[objType] || []
  const found = opts.find((o) => o.value === field)
  return found?.label || field
}

function parseFields(fields: string): string[] {
  try {
    return JSON.parse(fields) || []
  } catch {
    return []
  }
}

function resetForm() {
  form.name = ''
  form.object_type = 'account'
  form.is_active = true
  form.matching_fields = '[]'
  selectedFields.value = []
}

async function loadData() {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/duplicate-rules?page=${page.value}&page_size=${pageSize.value}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('Failed to load')
    const data = await res.json()
    items.value = data.items || []
    total.value = data.total || 0
  } catch (e: any) {
    ElMessage.error('加载失败: ' + (e.message || ''))
  } finally {
    loading.value = false
  }
}

function openCreate() {
  dialog.isEdit = false
  dialog.editId = ''
  resetForm()
  dialog.visible = true
}

function openEdit(row: DuplicateRule) {
  dialog.isEdit = true
  dialog.editId = row.id
  form.name = row.name
  form.object_type = row.object_type
  form.is_active = row.is_active
  form.matching_fields = row.matching_fields
  selectedFields.value = parseFields(row.matching_fields)
  dialog.visible = true
}

async function handleSave() {
  if (!form.name || selectedFields.value.length === 0) {
    ElMessage.warning('请填写规则名称并选择匹配字段')
    return
  }

  form.matching_fields = JSON.stringify(selectedFields.value)

  try {
    const token = localStorage.getItem('access_token')
    const body = JSON.stringify({ ...form })
    const url = dialog.isEdit
      ? `/api/duplicate-rules/${dialog.editId}`
      : '/api/duplicate-rules'
    const method = dialog.isEdit ? 'PUT' : 'POST'

    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body,
    })

    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Save failed')
    }

    ElMessage.success(dialog.isEdit ? '规则已更新' : '规则已创建')
    dialog.visible = false
    await loadData()
  } catch (e: any) {
    ElMessage.error('保存失败: ' + (e.message || ''))
  }
}

async function toggleActive(row: DuplicateRule) {
  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/duplicate-rules/${row.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ is_active: !row.is_active }),
    })
    if (!res.ok) throw new Error('Toggle failed')
    ElMessage.success(row.is_active ? '已禁用' : '已启用')
    await loadData()
  } catch (e: any) {
    ElMessage.error('操作失败: ' + (e.message || ''))
  }
}

async function handleDelete(row: DuplicateRule) {
  try {
    await ElMessageBox.confirm(
      `确定要删除规则「${row.name}」吗？`,
      '确认删除',
      { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }

  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/duplicate-rules/${row.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('Delete failed')
    ElMessage.success('已删除')
    await loadData()
  } catch (e: any) {
    ElMessage.error('删除失败: ' + (e.message || ''))
  }
}

onMounted(loadData)
</script>

<style scoped>
.duplicate-rule-page {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.page-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #080707;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>