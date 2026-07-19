<template>
  <div class="notification-list" v-loading="loading">
    <div class="nl-header">
      <h3 class="nl-title">通知列表</h3>
      <el-button v-if="hasUnread" size="small" @click="handleMarkAllRead">全部标记已读</el-button>
    </div>

    <el-table :data="notifications" border style="width:100%" @row-click="handleRowClick">
      <el-table-column label="状态" width="60" align="center">
        <template #default="{ row }">
          <el-icon v-if="!row.is_read" color="#1589ee" size="12"><circle-check /></el-icon>
        </template>
      </el-table-column>
      <el-table-column label="类型" width="80" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.notification_type === 'workflow'" size="small" type="warning">工作流</el-tag>
          <el-tag v-else size="small" type="info">系统</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="标题" prop="title" min-width="200" />
      <el-table-column label="内容" prop="message" min-width="250" show-overflow-tooltip />
      <el-table-column label="时间" width="160">
        <template #default="{ row }">
          {{ row.created_at ? new Date(row.created_at).toLocaleString('zh-CN') : '-' }}
        </template>
      </el-table-column>
    </el-table>

    <div class="nl-pagination" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadNotifications"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { CircleCheck } from '@element-plus/icons-vue'
import { notificationsApi } from '../../api/notifications'
import { useNotifications } from '../../composables/useNotifications'
import type { Notification } from '../../types/notification'

const router = useRouter()
const { markAsRead, markAllRead, unreadCount } = useNotifications()
const notifications = ref<Notification[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)
const hasUnread = computed(() => unreadCount.value > 0)

async function loadNotifications() {
  loading.value = true
  try {
    const { data } = await notificationsApi.list(page.value, pageSize)
    notifications.value = data.items
    total.value = data.total
  } catch {
    // silent
  } finally {
    loading.value = false
  }
}

async function handleRowClick(row: Notification) {
  if (!row.is_read) {
    await markAsRead(row.id)
    row.is_read = true
  }
  if (row.reference_type && row.reference_id) {
    const routes: Record<string, string> = {
      account: `/accounts/${row.reference_id}`,
      contact: `/contacts/${row.reference_id}`,
      opportunity: `/opportunities/${row.reference_id}`,
      territory: `/admin/territories`,
    }
    const path = routes[row.reference_type]
    if (path) router.push(path)
  }
}

function handleMarkAllRead() {
  markAllRead()
  notifications.value.forEach(n => { n.is_read = true })
}

onMounted(loadNotifications)
</script>

<style scoped>
.notification-list { padding: 16px; }
.nl-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 16px;
}
.nl-title { margin: 0; font-size: 16px; color: #333; }
.nl-pagination { margin-top: 16px; text-align: center; }
</style>