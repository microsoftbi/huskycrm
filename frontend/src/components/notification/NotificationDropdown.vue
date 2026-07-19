<template>
  <div class="notif-dropdown">
    <div class="notif-header">
      <span class="notif-title">通知</span>
      <el-button v-if="hasUnread" text size="small" @click="handleMarkAllRead">
        全部标记已读
      </el-button>
    </div>
    <div class="notif-list" v-loading="loading">
      <div v-if="items.length === 0" class="notif-empty">暂无通知</div>
      <div
        v-for="item in items"
        :key="item.id"
        class="notif-item"
        :class="{ 'notif-unread': !item.is_read }"
        @click="handleClick(item)"
      >
        <div class="notif-item-dot" v-if="!item.is_read" />
        <div class="notif-item-content">
          <div class="notif-item-title">{{ item.title }}</div>
          <div class="notif-item-message" v-if="item.message">{{ item.message }}</div>
          <div class="notif-item-time">{{ formatTime(item.created_at) }}</div>
        </div>
        <el-tag v-if="item.notification_type === 'workflow'" size="small" type="warning">工作流</el-tag>
      </div>
    </div>
    <div class="notif-footer">
      <router-link to="/admin/notifications" class="notif-footer-link">查看全部通知</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useNotifications } from '../../composables/useNotifications'

const router = useRouter()
const { recentNotifications: items, markAsRead, markAllRead } = useNotifications()

const loading = computed(() => false)
const hasUnread = computed(() => items.value.some(n => !n.is_read))

function formatTime(dateStr: string | null): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

async function handleClick(item: any) {
  if (!item.is_read) {
    await markAsRead(item.id)
  }
  if (item.reference_type && item.reference_id) {
    const routes: Record<string, string> = {
      account: `/accounts/${item.reference_id}`,
      contact: `/contacts/${item.reference_id}`,
      opportunity: `/opportunities/${item.reference_id}`,
      territory: `/admin/territories`,
    }
    const path = routes[item.reference_type]
    if (path) router.push(path)
  }
}

function handleMarkAllRead() {
  markAllRead()
}
</script>

<style scoped>
.notif-dropdown { font-size: 13px; }
.notif-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 14px; border-bottom: 1px solid #ebeef5;
}
.notif-title { font-weight: 600; color: #333; }
.notif-list { max-height: 360px; overflow-y: auto; }
.notif-empty { padding: 30px; text-align: center; color: #909399; }
.notif-item {
  display: flex; align-items: flex-start; gap: 8px;
  padding: 10px 14px; cursor: pointer; transition: background 0.1s;
  border-bottom: 1px solid #f2f2f2;
}
.notif-item:hover { background: #f5f7fa; }
.notif-unread { background: #f0f7ff; }
.notif-item-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #1589ee; flex-shrink: 0; margin-top: 5px;
}
.notif-item-content { flex: 1; min-width: 0; }
.notif-item-title { font-weight: 500; color: #333; margin-bottom: 2px; }
.notif-item-message { font-size: 12px; color: #909399; margin-bottom: 2px; }
.notif-item-time { font-size: 11px; color: #c0c4cc; }
.notif-footer {
  padding: 8px 14px; text-align: center; border-top: 1px solid #ebeef5;
}
.notif-footer-link { color: #1589ee; text-decoration: none; font-size: 12px; }
</style>