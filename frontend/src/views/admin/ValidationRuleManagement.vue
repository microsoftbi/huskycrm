<template>
  <div class="validation-rule-page">
    <div class="page-header">
      <h3>验证规则</h3>
      <el-button size="small" type="primary" @click="openCreate">新建规则</el-button>
    </div>

    <!-- List -->
    <el-table :data="items" v-loading="loading" stripe style="width: 100%">
      <el-table-column prop="name" label="规则名称" min-width="160" />
      <el-table-column prop="object_type" label="对象" width="120">
        <template #default="{ row }">
          {{ typeLabel(row.object_type) }}
        </template>
      </el-table-column>
      <el-table-column prop="error_message" label="错误消息" min-width="200">
        <template #default="{ row }">
          <el-tooltip :content="row.error_message" placement="top">
            <span class="ellipsis-text">{{ row.error_message }}</span>
          </el-tooltip>
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

    <!-- Pagination -->
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
      :title="dialog.isEdit ? '编辑验证规则' : '新建验证规则'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" label-width="100px" size="small">
        <el-form-item label="规则名称" required>
          <el-input v-model="form.name" placeholder="如：商机金额不能超过100万" />
        </el-form-item>
        <el-form-item label="对象" required>
          <el-select v-model="form.object_type" style="width: 100%">
            <el-option label="账户" value="account" />
            <el-option label="联系人" value="contact" />
            <el-option label="销售机会" value="opportunity" />
            <el-option label="产品" value="product" />
          </el-select>
        </el-form-item>
        <el-form-item label="条件" required>
          <div class="conditions-editor">
            <div class="condition-help">
              条件格式：JSON 数组，每个条件包含 field, operator, value
            </div>
            <el-input
              v-model="form.condition_expression"
              type="textarea"
              :rows="6"
              placeholder='[{"field": "amount", "operator": "gt", "value": 1000000}]'
            />
            <div class="condition-examples">
              <span class="example-label">示例：</span>
              <el-tag size="small" @click="insertExample('amount_gt')">金额 > 100万</el-tag>
              <el-tag size="small" @click="insertExample('amount_lt')">金额 < 0</el-tag>
              <el-tag size="small" @click="insertExample('name_empty')">名称不能为空</el-tag>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="错误消息" required>
          <el-input
            v-model="form.error_message"
            placeholder="如：商机金额不能超过 1,000,000"
          />
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface ValidationRule {
  id: string
  name: string
  object_type: string
  is_active: boolean
  condition_expression: string
  error_message: string
  created_at: string
  updated_at: string
}

const loading = ref(false)
const items = ref<ValidationRule[]>([])
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
  condition_expression: '[]',
  error_message: '',
})

const TYPE_LABELS: Record<string, string> = {
  account: '账户',
  contact: '联系人',
  opportunity: '销售机会',
  product: '产品',
}

function typeLabel(type: string): string {
  return TYPE_LABELS[type] || type
}

function resetForm() {
  form.name = ''
  form.object_type = 'account'
  form.is_active = true
  form.condition_expression = '[]'
  form.error_message = ''
}

function insertExample(type: string) {
  const examples: Record<string, string> = {
    amount_gt: '[{"field": "amount", "operator": "gt", "value": 1000000}]',
    amount_lt: '[{"field": "amount", "operator": "lt", "value": 0}]',
    name_empty: '[{"field": "name", "operator": "is_empty", "value": ""}]',
  }
  form.condition_expression = examples[type] || '[]'
}

async function loadData() {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/validation-rules?page=${page.value}&page_size=${pageSize.value}`, {
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

function openEdit(row: ValidationRule) {
  dialog.isEdit = true
  dialog.editId = row.id
  form.name = row.name
  form.object_type = row.object_type
  form.is_active = row.is_active
  form.condition_expression = row.condition_expression
  form.error_message = row.error_message
  dialog.visible = true
}

async function handleSave() {
  if (!form.name || !form.error_message) {
    ElMessage.warning('请填写规则名称和错误消息')
    return
  }

  try {
    const token = localStorage.getItem('access_token')
    const body = JSON.stringify({ ...form })
    const url = dialog.isEdit
      ? `/api/validation-rules/${dialog.editId}`
      : '/api/validation-rules'
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

async function toggleActive(row: ValidationRule) {
  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/validation-rules/${row.id}`, {
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

async function handleDelete(row: ValidationRule) {
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
    const res = await fetch(`/api/validation-rules/${row.id}`, {
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
.validation-rule-page {
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

.conditions-editor {
  width: 100%;
}

.condition-help {
  font-size: 12px;
  color: #706e6b;
  margin-bottom: 6px;
}

.condition-examples {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.example-label {
  font-size: 12px;
  color: #706e6b;
}

.condition-examples .el-tag {
  cursor: pointer;
}

.ellipsis-text {
  display: inline-block;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>