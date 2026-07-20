<template>
  <div class="approval-queue-page">
    <div class="page-header">
      <h2>我的审批</h2>
    </div>

    <!-- Status tabs -->
    <el-tabs v-model="statusFilter" @tab-change="loadData">
      <el-tab-pane label="待审批" name="pending" />
      <el-tab-pane label="全部" name="" />
    </el-tabs>

    <!-- Queue Items -->
    <div v-loading="loading">
      <div v-for="item in items" :key="item.id" class="approval-card">
        <div class="approval-card-header">
          <div class="approval-info">
            <el-tag :type="statusTag(item.status)" size="small">
              {{ statusLabel(item.status) }}
            </el-tag>
            <span class="approval-object-type">{{ typeLabel(item.object_type) }}</span>
            <span class="approval-object-name">{{ item.object_name }}</span>
          </div>
          <div class="approval-step">
            步骤 {{ item.current_step }} / {{ item.total_steps }}
          </div>
        </div>
        <div class="approval-card-body">
          <div class="approval-meta">
            <span class="meta-label">提交人：</span>
            <span>{{ item.submitter_name || item.submitter_id }}</span>
          </div>
          <div class="approval-meta">
            <span class="meta-label">提交时间：</span>
            <span>{{ formatDate(item.created_at) }}</span>
          </div>
          <div class="approval-meta">
            <span class="meta-label">审批规则：</span>
            <span>{{ item.rule_name || item.rule_id }}</span>
          </div>
        </div>

        <!-- Action buttons for pending items -->
        <div v-if="item.status === 'pending'" class="approval-card-actions">
          <el-input
            v-model="commentMap[item.id]"
            placeholder="审批意见（可选）"
            size="small"
            style="width: 300px; margin-right: 8px"
          />
          <el-button size="small" type="success" @click="handleApprove(item)">
            批准
          </el-button>
          <el-button size="small" type="danger" @click="handleReject(item)">
            驳回
          </el-button>
        </div>

        <!-- Show comment for processed items -->
        <div v-else-if="item.steps && item.steps.length > 0" class="approval-card-steps">
          <div v-for="step in item.steps" :key="step.id" class="step-item">
            <el-tag :type="step.status === 'approved' ? 'success' : 'danger'" size="small">
              {{ step.status === 'approved' ? '已批准' : '已驳回' }}
            </el-tag>
            <span class="step-comment">{{ step.comment || '无意见' }}</span>
            <span class="step-time">{{ formatDate(step.acted_at) }}</span>
          </div>
        </div>
      </div>

      <el-empty v-if="!loading && items.length === 0" description="暂无审批记录" />
    </div>

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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

interface ApprovalStep {
  id: string
  step_order: number
  approver_id: string
  approver_name: string | null
  status: string
  comment: string | null
  acted_at: string | null
  created_at: string
}

interface ApprovalRequest {
  id: string
  rule_id: string
  rule_name: string | null
  object_type: string
  object_id: string
  object_name: string | null
  submitter_id: string
  submitter_name: string | null
  status: string
  current_step: number
  total_steps: number
  created_at: string
  updated_at: string
  steps: ApprovalStep[]
}

const loading = ref(false)
const items = ref<ApprovalRequest[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const statusFilter = ref('pending')
const commentMap = reactive<Record<string, string>>({})

function typeLabel(type: string): string {
  const labels: Record<string, string> = { opportunity: '商机' }
  return labels[type] || type
}

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    pending: '待审批',
    approved: '已批准',
    rejected: '已驳回',
    cancelled: '已取消',
  }
  return labels[status] || status
}

function statusTag(status: string): string {
  const tags: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
  }
  return tags[status] || ''
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function loadData() {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const params = new URLSearchParams({
      page: page.value.toString(),
      page_size: pageSize.value.toString(),
    })
    if (statusFilter.value) params.set('status_filter', statusFilter.value)

    const res = await fetch(`/api/approval-rules/my-queue?${params}`, {
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

async function handleApprove(item: ApprovalRequest) {
  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/approval-rules/requests/${item.id}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ comment: commentMap[item.id] || null }),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Approve failed')
    }
    ElMessage.success('已批准')
    delete commentMap[item.id]
    await loadData()
  } catch (e: any) {
    ElMessage.error('操作失败: ' + (e.message || ''))
  }
}

async function handleReject(item: ApprovalRequest) {
  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/approval-rules/requests/${item.id}/reject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ comment: commentMap[item.id] || null }),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Reject failed')
    }
    ElMessage.success('已驳回')
    delete commentMap[item.id]
    await loadData()
  } catch (e: any) {
    ElMessage.error('操作失败: ' + (e.message || ''))
  }
}

onMounted(loadData)
</script>

<style scoped>
.approval-queue-page {
  background: #fff;
  border: 1px solid #dddbda;
  border-radius: 3px;
  padding: 20px;
}

.page-header {
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #080707;
}

.approval-card {
  border: 1px solid #dddbda;
  border-radius: 3px;
  margin-bottom: 12px;
  padding: 14px;
}

.approval-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.approval-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.approval-object-type {
  font-size: 12px;
  color: #706e6b;
}

.approval-object-name {
  font-size: 14px;
  font-weight: 600;
  color: #080707;
}

.approval-step {
  font-size: 12px;
  color: #706e6b;
}

.approval-card-body {
  margin-bottom: 10px;
}

.approval-meta {
  font-size: 12px;
  color: #514f4d;
  margin-bottom: 4px;
}

.meta-label {
  color: #706e6b;
}

.approval-card-actions {
  display: flex;
  align-items: center;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

.approval-card-steps {
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  margin-bottom: 4px;
}

.step-comment {
  color: #514f4d;
}

.step-time {
  color: #706e6b;
  font-size: 11px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>