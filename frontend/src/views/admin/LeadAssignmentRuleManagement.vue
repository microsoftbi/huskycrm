<template>
  <div class="assignment-rule-page">
    <div class="page-header">
      <h3>线索分配规则</h3>
      <el-button size="small" type="primary" @click="openCreate">新建规则</el-button>
    </div>

    <el-table :data="items" v-loading="loading" stripe style="width: 100%">
      <el-table-column prop="name" label="规则名称" min-width="160" />
      <el-table-column prop="assign_to_user_name" label="分配给" min-width="140" />
      <el-table-column prop="priority" label="优先级" width="80" align="center" />
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="page" :page-size="pageSize" :total="total"
        layout="total, prev, pager, next" small @current-change="loadData"
      />
    </div>

    <!-- Dialog -->
    <el-dialog v-model="dialog.visible" :title="dialog.isEdit ? '编辑规则' : '新建规则'" width="600px" :close-on-click-modal="false">
      <el-form :model="form" label-width="100px" size="small">
        <el-form-item label="规则名称" required>
          <el-input v-model="form.name" placeholder="如：网站线索自动分配" />
        </el-form-item>
        <el-form-item label="条件" required>
          <el-input v-model="form.condition_expression" type="textarea" :rows="4"
            placeholder='[{"field": "source", "operator": "eq", "value": "Web"}]' />
          <div class="condition-examples" style="margin-top:6px">
            <el-tag size="small" @click="setCondition('source', 'eq', 'Web')">来源=网站</el-tag>
            <el-tag size="small" @click="setCondition('industry', 'eq', '科技')">行业=科技</el-tag>
          </div>
        </el-form-item>
        <el-form-item label="分配给" required>
          <el-select v-model="form.assign_to_user_id" filterable placeholder="选择用户..." style="width: 100%">
            <el-option v-for="u in userOptions" :key="u.id" :label="u.display_name || u.username" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-input-number v-model="form.priority" :min="0" :max="100" />
          <span class="form-help">值越大优先匹配</span>
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

interface Rule {
  id: string; name: string; is_active: boolean; condition_expression: string
  assign_to_user_id: string; assign_to_user_name: string | null; priority: number
}

const loading = ref(false)
const items = ref<Rule[]>([])
const total = ref(0); const page = ref(1); const pageSize = ref(20)
const userOptions = ref<{ id: string; username: string; display_name: string }[]>([])

const dialog = reactive({ visible: false, isEdit: false, editId: '' })
const form = reactive({ name: '', is_active: true, condition_expression: '[]', assign_to_user_id: '', priority: 0 })

function resetForm() {
  form.name = ''; form.is_active = true; form.condition_expression = '[]'; form.assign_to_user_id = ''; form.priority = 0
}

function setCondition(field: string, op: string, val: string) {
  form.condition_expression = JSON.stringify([{field, operator: op, value: val}])
}

async function loadUsers() {
  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch('/api/users?page_size=100', { headers: { Authorization: `Bearer ${token}` } })
    if (res.ok) { const d = await res.json(); userOptions.value = d.items || [] }
  } catch { /* ignore */ }
}

async function loadData() {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/leads/assignment-rules?page=${page.value}&page_size=${pageSize.value}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('Failed to load')
    const data = await res.json()
    items.value = data.items || []
    total.value = data.total || 0
  } catch (e: any) { ElMessage.error('加载失败: ' + (e.message || ''))
  } finally { loading.value = false }
}

function openCreate() { dialog.isEdit = false; dialog.editId = ''; resetForm(); dialog.visible = true; loadUsers() }
function openEdit(row: Rule) {
  dialog.isEdit = true; dialog.editId = row.id
  form.name = row.name; form.is_active = row.is_active; form.condition_expression = row.condition_expression
  form.assign_to_user_id = row.assign_to_user_id; form.priority = row.priority
  dialog.visible = true; loadUsers()
}

async function handleSave() {
  if (!form.name || !form.assign_to_user_id) { ElMessage.warning('请填写规则名称和分配用户'); return }
  try {
    const token = localStorage.getItem('access_token')
    const body = JSON.stringify({ ...form })
    const url = dialog.isEdit ? `/api/leads/assignment-rules/${dialog.editId}` : '/api/leads/assignment-rules'
    const method = dialog.isEdit ? 'PUT' : 'POST'
    const res = await fetch(url, { method, headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }, body })
    if (!res.ok) { const err = await res.json(); throw new Error(err.detail || 'Save failed') }
    ElMessage.success(dialog.isEdit ? '规则已更新' : '规则已创建')
    dialog.visible = false
    await loadData()
  } catch (e: any) { ElMessage.error('保存失败: ' + (e.message || '')) }
}

async function handleDelete(row: Rule) {
  try { await ElMessageBox.confirm(`确定删除规则「${row.name}」吗？`, '确认删除', { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }) } catch { return }
  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/leads/assignment-rules/${row.id}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } })
    if (!res.ok) throw new Error('Delete failed')
    ElMessage.success('已删除'); await loadData()
  } catch (e: any) { ElMessage.error('删除失败: ' + (e.message || '')) }
}

onMounted(loadData)
</script>

<style scoped>
.assignment-rule-page { padding: 0; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h3 { margin: 0; font-size: 16px; font-weight: 700; color: #080707; }
.pagination-wrapper { display: flex; justify-content: flex-end; margin-top: 16px; }
.form-help { font-size: 11px; color: #706e6b; margin-left: 8px; }
.condition-examples .el-tag { cursor: pointer; margin-right: 4px; }
</style>