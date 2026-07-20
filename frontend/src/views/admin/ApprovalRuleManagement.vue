<template>
  <div class="approval-rule-page">
    <div class="page-header">
      <h3>审批规则</h3>
      <el-button size="small" type="primary" @click="openCreate">新建规则</el-button>
    </div>

    <el-table :data="items" v-loading="loading" stripe style="width: 100%">
      <el-table-column prop="name" label="规则名称" min-width="160" />
      <el-table-column prop="object_type" label="对象" width="100">
        <template #default="{ row }">
          {{ typeLabel(row.object_type) }}
        </template>
      </el-table-column>
      <el-table-column prop="approver_type" label="审批人类型" width="120">
        <template #default="{ row }">
          {{ approverTypeLabel(row.approver_type) }}
        </template>
      </el-table-column>
      <el-table-column prop="approval_order" label="审批层级" width="80" />
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
      :title="dialog.isEdit ? '编辑审批规则' : '新建审批规则'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" label-width="100px" size="small">
        <el-form-item label="规则名称" required>
          <el-input v-model="form.name" placeholder="如：商机金额超100万需审批" />
        </el-form-item>
        <el-form-item label="对象" required>
          <el-select v-model="form.object_type" style="width: 100%">
            <el-option label="销售机会" value="opportunity" />
          </el-select>
        </el-form-item>
        <el-form-item label="条件" required>
          <el-input
            v-model="form.condition_expression"
            type="textarea"
            :rows="4"
            placeholder='[{"field": "amount", "operator": "gt", "value": 100000}]'
          />
          <div class="condition-examples">
            <el-tag size="small" @click="setCondition(100000)">
              金额 > 10万
            </el-tag>
            <el-tag size="small" @click="setCondition(500000)">
              金额 > 50万
            </el-tag>
          </div>
        </el-form-item>
        <el-form-item label="审批人类型" required>
          <el-select v-model="form.approver_type" style="width: 100%">
            <el-option label="系统管理员" value="manager" />
            <el-option label="指定用户" value="specific_user" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="form.approver_type === 'specific_user'" label="审批人" required>
          <el-input v-model="form.approver_user_id" placeholder="用户ID" />
        </el-form-item>
        <el-form-item label="审批层级" required>
          <el-input-number v-model="form.approval_order" :min="1" :max="10" />
          <span class="form-help">数字越小优先级越高，第1级审批通过后进入第2级</span>
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

interface ApprovalRule {
  id: string
  name: string
  object_type: string
  is_active: boolean
  condition_expression: string
  approver_type: string
  approver_user_id: string | null
  approval_order: number
  created_at: string
  updated_at: string
}

const loading = ref(false)
const items = ref<ApprovalRule[]>([])
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
  object_type: 'opportunity',
  is_active: true,
  condition_expression: '[]',
  approver_type: 'manager',
  approver_user_id: null as string | null,
  approval_order: 1,
})

function typeLabel(type: string): string {
  const labels: Record<string, string> = { opportunity: '销售机会' }
  return labels[type] || type
}

function approverTypeLabel(type: string): string {
  const labels: Record<string, string> = { manager: '系统管理员', specific_user: '指定用户' }
  return labels[type] || type
}

function resetForm() {
  form.name = ''
  form.object_type = 'opportunity'
  form.is_active = true
  form.condition_expression = '[]'
  form.approver_type = 'manager'
  form.approver_user_id = null
  form.approval_order = 1
}

function setCondition(amount: number) {
  form.condition_expression = JSON.stringify([{field: 'amount', operator: 'gt', value: amount}])
}

async function loadData() {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/approval-rules?page=${page.value}&page_size=${pageSize.value}`, {
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

function openEdit(row: ApprovalRule) {
  dialog.isEdit = true
  dialog.editId = row.id
  form.name = row.name
  form.object_type = row.object_type
  form.is_active = row.is_active
  form.condition_expression = row.condition_expression
  form.approver_type = row.approver_type
  form.approver_user_id = row.approver_user_id
  form.approval_order = row.approval_order
  dialog.visible = true
}

async function handleSave() {
  if (!form.name || !form.condition_expression) {
    ElMessage.warning('请填写规则名称和条件')
    return
  }

  try {
    const token = localStorage.getItem('access_token')
    const body = JSON.stringify({ ...form })
    const url = dialog.isEdit
      ? `/api/approval-rules/${dialog.editId}`
      : '/api/approval-rules'
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

async function toggleActive(row: ApprovalRule) {
  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/approval-rules/${row.id}`, {
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

async function handleDelete(row: ApprovalRule) {
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
    const res = await fetch(`/api/approval-rules/${row.id}`, {
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
.approval-rule-page {
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

.condition-examples {
  margin-top: 6px;
  display: flex;
  gap: 6px;
}

.condition-examples .el-tag {
  cursor: pointer;
}

.form-help {
  font-size: 11px;
  color: #706e6b;
  margin-left: 8px;
}
</style>