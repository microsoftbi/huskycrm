<template>
  <div class="workflow-list">
    <div class="list-header">
      <h2 class="page-title">工作流规则</h2>
      <router-link to="/admin/workflows/new">
        <el-button type="primary" icon="plus">新建规则</el-button>
      </router-link>
    </div>

    <el-card shadow="hover">
      <el-table :data="rules" stripe v-loading="loading" style="width: 100%">
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="name" label="名称" min-width="180" />
        <el-table-column prop="object_type" label="对象" width="120" />
        <el-table-column label="触发事件" width="120">
          <template #default="{ row }">{{ triggerLabels[row.trigger_event] || row.trigger_event }}</template>
        </el-table-column>
        <el-table-column label="条件" width="180">
          <template #default="{ row }">{{ row.condition_expression?.length || 0 }} 个条件</template>
        </el-table-column>
        <el-table-column label="动作" width="120">
          <template #default="{ row }">{{ row.actions?.length || 0 }} 个动作</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              :model-value="row.is_active"
              @change="toggleActive(row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/admin/workflows/${row.id}`)">编辑</el-button>
            <el-button size="small" type="danger" plain @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && rules.length === 0" description="暂无工作流规则" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { workflowsApi, type WorkflowRule } from '../../api/workflows'

const rules = ref<WorkflowRule[]>([])
const loading = ref(false)
const triggerLabels: Record<string, string> = {
  create: '创建时', update: '更新时', create_or_update: '创建或更新',
}

async function fetchRules() {
  loading.value = true
  try {
    const { data } = await workflowsApi.list()
    rules.value = data
  } finally { loading.value = false }
}

async function toggleActive(row: WorkflowRule) {
  try {
    await workflowsApi.update(row.id, { is_active: !row.is_active })
    row.is_active = !row.is_active
    ElMessage.success(row.is_active ? '已启用' : '已停用')
  } catch { ElMessage.error('操作失败') }
}

async function handleDelete(row: WorkflowRule) {
  try {
    await ElMessageBox.confirm(`确定删除规则 "${row.name}" 吗？`, '确认删除', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
    await workflowsApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchRules()
  } catch { /* cancelled */ }
}

onMounted(fetchRules)
</script>

<style scoped>
.workflow-list { max-width: 1200px; }
.list-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
}
.page-title { margin: 0; font-size: 22px; color: #333; }
</style>