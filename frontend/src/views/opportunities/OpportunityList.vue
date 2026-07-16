<template>
  <div class="opportunity-list">
    <div class="sf-page-header">
      <h2 class="sf-page-title">销售机会</h2>
      <div class="sf-page-actions">
        <router-link to="/opportunities/pipeline">
          <el-button size="small" icon="s-grid">管道看板</el-button>
        </router-link>
        <router-link to="/opportunities/new">
          <el-button type="primary" size="small" icon="plus">新建机会</el-button>
        </router-link>
      </div>
    </div>

    <div class="sf-card">
      <div class="sf-filter-bar">
        <el-input v-model="searchQuery" placeholder="搜索机会名称..." clearable size="small" @clear="fetchOpportunities" @keyup.enter="fetchOpportunities">
          <template #prefix><el-icon><search /></el-icon></template>
        </el-input>
        <el-select v-model="stageFilter" placeholder="按阶段筛选" clearable size="small" style="width:180px" @change="fetchOpportunities">
          <el-option v-for="s in stages" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>
      </div>

      <el-table :data="opportunities" stripe v-loading="loading" class="sf-table-compact" size="small" style="width:100%">
        <el-table-column type="index" label="#" width="60" />
        <el-table-column label="名称" min-width="200">
          <template #default="{ row }">
            <router-link :to="`/opportunities/${row.id}`"><el-link type="primary">{{ row.name }}</el-link></router-link>
          </template>
        </el-table-column>
        <el-table-column label="金额" width="140">
          <template #default="{ row }">¥{{ (row.amount || 0).toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="阶段" width="120">
          <template #default="{ row }">
            <el-tag :type="getStageTag(row.stage_id)" size="small">{{ getStageName(row.stage_id) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="概率" width="80">
          <template #default="{ row }">{{ row.probability || 0 }}%</template>
        </el-table-column>
        <el-table-column label="预计关闭日" width="140">
          <template #default="{ row }">{{ row.close_date || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/opportunities/${row.id}`)">查看</el-button>
            <el-button size="small" type="danger" plain @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="padding:10px 14px;display:flex;justify-content:flex-end;border-top:1px solid #dddbda;">
        <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total, sizes, prev, pager, next" size="small" @change="fetchOpportunities" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { opportunitiesApi } from '../../api/opportunities'
import type { Opportunity, Stage } from '../../types/crm'

const opportunities = ref<Opportunity[]>([])
const stages = ref<Stage[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const searchQuery = ref('')
const stageFilter = ref<number | undefined>()
const stageMap = ref<Record<number, Stage>>({})

function getStageName(stageId: number) { return stageMap.value[stageId]?.name || '-' }
function getStageTag(stageId: number) {
  const s = stageMap.value[stageId]
  if (!s) return 'info'
  if (s.is_closed_won) return 'success'
  if (s.is_closed_lost) return 'danger'
  if (s.probability >= 70) return 'warning'
  return 'primary'
}

async function fetchStages() {
  try {
    const { data } = await opportunitiesApi.getStages()
    stages.value = data
    data.forEach(s => { stageMap.value[s.id] = s })
  } catch { /* ignore */ }
}

async function fetchOpportunities() {
  loading.value = true
  try {
    const { data } = await opportunitiesApi.list({ page: page.value, page_size: pageSize.value, search: searchQuery.value, stage_id: stageFilter.value })
    opportunities.value = data.items
    total.value = data.total
  } finally { loading.value = false }
}

async function handleDelete(row: Opportunity) {
  try {
    await ElMessageBox.confirm(`确定删除机会 "${row.name}" 吗？`, '确认删除', {
      confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning',
    })
    await opportunitiesApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchOpportunities()
  } catch { /* cancelled */ }
}

onMounted(async () => { await fetchStages(); await fetchOpportunities() })
</script>

<style scoped>
.opportunity-list { max-width: 1200px; }
</style>
