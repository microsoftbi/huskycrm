<template>
  <div class="campaign-list-page">
    <!-- Header -->
    <div class="page-header">
      <h2>活动管理</h2>
      <el-button type="primary" size="small" icon="plus" @click="createNew">新建活动</el-button>
    </div>

    <!-- Filters -->
    <div class="filters">
      <el-input
        v-model="search"
        placeholder="搜索活动名称..."
        size="small"
        clearable
        style="width: 200px"
        @clear="loadData"
        @keyup.enter="loadData"
      />
      <el-select v-model="statusFilter" placeholder="状态" clearable size="small" style="width: 120px" @change="loadData">
        <el-option label="全部" value="" />
        <el-option label="规划中" value="planning" />
        <el-option label="进行中" value="in_progress" />
        <el-option label="已完成" value="completed" />
        <el-option label="已取消" value="cancelled" />
      </el-select>
      <el-select v-model="typeFilter" placeholder="类型" clearable size="small" style="width: 120px" @change="loadData">
        <el-option label="全部" value="" />
        <el-option label="会议" value="conference" />
        <el-option label="展览" value="exhibition" />
        <el-option label="邮件" value="email" />
        <el-option label="广告" value="ad" />
        <el-option label="其他" value="other" />
      </el-select>
      <el-button size="small" type="primary" @click="loadData">搜索</el-button>
    </div>

    <!-- Table -->
    <el-table :data="items" v-loading="loading" stripe style="width: 100%">
      <el-table-column prop="name" label="活动名称" min-width="180">
        <template #default="{ row }">
          <router-link :to="`/campaigns/${row.id}`" class="record-link">{{ row.name }}</router-link>
        </template>
      </el-table-column>
      <el-table-column prop="type" label="类型" width="100">
        <template #default="{ row }">
          <el-tag size="small">{{ typeLabel(row.type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusTag(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="budget" label="预算" width="120">
        <template #default="{ row }">
          {{ row.budget ? '¥' + formatNumber(row.budget) : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="member_count" label="成员数" width="80" align="center" />
      <el-table-column prop="converted_opportunities" label="转化商机" width="120" align="center" />
      <el-table-column prop="roi" label="ROI" width="100">
        <template #default="{ row }">
          <span v-if="row.roi !== null" :class="roiClass(row.roi)">{{ row.roi }}%</span>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="editCampaign(row)">编辑</el-button>
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
        @current-change="loadData"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

interface Campaign {
  id: string
  name: string
  type: string
  status: string
  budget: number | null
  actual_cost: number | null
  member_count: number
  converted_opportunities: number
  converted_amount: number
  roi: number | null
  created_at: string
  updated_at: string
}

const router = useRouter()
const loading = ref(false)
const items = ref<Campaign[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const search = ref('')
const statusFilter = ref('')
const typeFilter = ref('')

function typeLabel(type: string): string {
  const labels: Record<string, string> = { conference: '会议', exhibition: '展览', email: '邮件', ad: '广告', other: '其他' }
  return labels[type] || type
}

function statusLabel(status: string): string {
  const labels: Record<string, string> = { planning: '规划中', in_progress: '进行中', completed: '已完成', cancelled: '已取消' }
  return labels[status] || status
}

function statusTag(status: string): string {
  const tags: Record<string, string> = { planning: 'info', in_progress: 'warning', completed: 'success', cancelled: 'danger' }
  return tags[status] || ''
}

function roiClass(roi: number): string {
  if (roi > 500) return 'roi-excellent'
  if (roi > 200) return 'roi-good'
  if (roi > 0) return 'roi-normal'
  return 'roi-bad'
}

function formatNumber(n: number): string {
  return n.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function loadData() {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const params = new URLSearchParams({
      page: page.value.toString(),
      page_size: pageSize.value.toString(),
    })
    if (search.value) params.set('search', search.value)
    if (statusFilter.value) params.set('status_filter', statusFilter.value)
    if (typeFilter.value) params.set('type_filter', typeFilter.value)

    const res = await fetch(`/api/campaigns?${params}`, {
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

function createNew() {
  router.push('/campaigns/new')
}

function editCampaign(row: Campaign) {
  router.push(`/campaigns/${row.id}/edit`)
}

async function handleDelete(row: Campaign) {
  try {
    await ElMessageBox.confirm(
      `确定要删除活动「${row.name}」吗？`,
      '确认删除',
      { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }

  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/campaigns/${row.id}`, {
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
.campaign-list-page {
  background: #fff;
  border: 1px solid #dddbda;
  border-radius: 3px;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #080707;
}

.filters {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  align-items: center;
}

.record-link {
  color: #1589ee;
  text-decoration: none;
  font-weight: 500;
}

.record-link:hover {
  text-decoration: underline;
}

.roi-excellent { color: #67c23a; font-weight: 600; }
.roi-good { color: #409eff; font-weight: 600; }
.roi-normal { color: #e6a23c; }
.roi-bad { color: #f56c6c; }

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>