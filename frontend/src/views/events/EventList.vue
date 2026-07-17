<template>
  <div class="event-list">
    <div class="sf-page-header">
      <h2 class="sf-page-title">拜访记录</h2>
      <el-button type="primary" size="small" @click="$router.push('/events/new')">
        <el-icon><plus /></el-icon> 新建拜访
      </el-button>
    </div>

    <!-- Filters -->
    <div class="sf-card" style="margin-bottom:12px;">
      <div class="sf-card-body">
        <el-row :gutter="12">
          <el-col :span="8">
            <el-input v-model="search" placeholder="搜索主题" clearable size="small" @input="onSearch" />
          </el-col>
          <el-col :span="5">
            <el-select v-model="statusFilter" placeholder="状态" clearable size="small" style="width:100%" @change="fetchData">
              <el-option label="计划中" value="planned" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="已完成" value="completed" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
          </el-col>
          <el-col :span="5">
            <el-select v-model="typeFilter" placeholder="类型" clearable size="small" style="width:100%" @change="fetchData">
              <el-option label="上门拜访" value="Visit" />
              <el-option label="电话拜访" value="Phone Call" />
              <el-option label="视频会议" value="Video Conference" />
              <el-option label="客户来访" value="Client Visit" />
              <el-option label="其他" value="Other" />
            </el-select>
          </el-col>
        </el-row>
      </div>
    </div>

    <!-- Table -->
    <div class="sf-card">
      <div class="sf-card-body" style="padding:0;">
        <el-table :data="events" v-loading="loading" stripe size="small" style="width:100%"
          @row-click="(row: any) => $router.push(`/events/${row.id}`)" highlight-current-row>
          <el-table-column label="主题" min-width="200">
            <template #default="{ row }">
              <router-link :to="`/events/${row.id}`" class="sf-link" @click.stop>
                {{ row.subject }}
              </router-link>
            </template>
          </el-table-column>
          <el-table-column label="类型" width="120">
            <template #default="{ row }">{{ typeLabel(row.type) }}</template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="计划时间" width="180">
            <template #default="{ row }">{{ formatTime(row.start_datetime) }}</template>
          </el-table-column>
          <el-table-column label="拜访结果" width="120">
            <template #default="{ row }">{{ outcomeLabel(row.outcome) }}</template>
          </el-table-column>
          <el-table-column label="创建时间" width="180">
            <template #default="{ row }">{{ row.created_at }}</template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- Pagination -->
    <div class="sf-pagination-wrapper">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        small
        @change="fetchData"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { eventsApi } from '../../api/events'
import type { Event } from '../../types/event'

const events = ref<Event[]>([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const search = ref('')
const statusFilter = ref('')
const typeFilter = ref('')

let searchTimer: ReturnType<typeof setTimeout> | null = null

function onSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    fetchData()
  }, 300)
}

async function fetchData() {
  loading.value = true
  try {
    const { data } = await eventsApi.list({
      page: page.value,
      page_size: pageSize.value,
      search: search.value,
      status_filter: statusFilter.value,
      type_filter: typeFilter.value,
    })
    events.value = data.items
    total.value = data.total
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

function formatTime(dt: string) {
  if (!dt) return '-'
  return dt.replace('T', ' ').substring(0, 16)
}

function typeLabel(t: string) {
  const labels: Record<string, string> = {
    'Visit': '上门拜访', 'Phone Call': '电话拜访',
    'Video Conference': '视频会议', 'Client Visit': '客户来访', 'Other': '其他',
  }
  return labels[t] || t
}

function statusLabel(s: string) {
  const labels: Record<string, string> = {
    'planned': '计划中', 'in_progress': '进行中',
    'completed': '已完成', 'cancelled': '已取消',
  }
  return labels[s] || s
}

function statusTagType(s: string) {
  const types: Record<string, string> = {
    'planned': 'info', 'in_progress': 'warning',
    'completed': 'success', 'cancelled': 'danger',
  }
  return types[s] || 'info'
}

function outcomeLabel(o: string | undefined | null) {
  const labels: Record<string, string> = {
    'success': '成功', 'neutral': '一般',
    'failure': '失败', 'no_show': '未出席',
  }
  return o ? (labels[o] || o) : '-'
}

onMounted(fetchData)
</script>

<style scoped>
.event-list { max-width: 1100px; }
.sf-link { color: #1589ee; text-decoration: none; }
.sf-link:hover { text-decoration: underline; }
.sf-pagination-wrapper { display: flex; justify-content: flex-end; padding: 12px 0; }
</style>
