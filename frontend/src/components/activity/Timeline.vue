<template>
  <div class="timeline" v-loading="loading">
    <div v-if="entries.length === 0" class="timeline-empty">
      <el-empty description="暂无活动记录" :image-size="60" />
    </div>
    <div v-else class="timeline-list">
      <template v-for="(group, gIdx) in groupedEntries" :key="gIdx">
        <div class="timeline-date-header">{{ group.date }}</div>
        <div
          v-for="(entry, eIdx) in group.entries"
          :key="`${gIdx}-${eIdx}`"
          class="timeline-item"
          :class="`timeline-type-${entry.type}`"
        >
          <div class="timeline-dot">
            <el-icon v-if="entry.type === 'audit'" :size="12"><edit-pen /></el-icon>
            <el-icon v-else-if="entry.type === 'event'" :size="12"><phone /></el-icon>
            <el-icon v-else :size="12"><check /></el-icon>
          </div>
          <div class="timeline-content">
            <div class="timeline-header">
              <span class="timeline-user">{{ entry.user_display_name || 'System' }}</span>
              <span class="timeline-time">{{ formatTime(entry.created_at) }}</span>
            </div>
            <div class="timeline-body">
              <template v-if="entry.type === 'audit'">
                <span v-if="entry.action === 'create'">创建了此记录</span>
                <span v-else-if="entry.action === 'delete'">删除了此记录</span>
                <span v-else-if="entry.action === 'update' && entry.field_name">
                  更新了 <strong>{{ fieldLabel(entry.field_name) }}</strong>
                  <span class="timeline-change" v-if="entry.old_value !== null">
                    {{ entry.old_value || '(空)' }} → {{ entry.new_value || '(空)' }}
                  </span>
                </span>
              </template>
              <template v-else-if="entry.type === 'event'">
                <span>完成了拜访 <strong>{{ entry.subject }}</strong></span>
                <el-tag v-if="entry.result" :type="resultType(entry.result)" size="small" class="timeline-tag">
                  {{ resultLabel(entry.result) }}
                </el-tag>
              </template>
              <template v-else>
                <span>完成任务 <strong>{{ entry.subject }}</strong></span>
              </template>
            </div>
          </div>
        </div>
      </template>

      <div v-if="hasMore" class="timeline-load-more">
        <el-button text type="primary" :loading="loadingMore" @click="$emit('load-more')">
          加载更多
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { EditPen, Phone, Check } from '@element-plus/icons-vue'
import type { TimelineEntry } from '../../types/auditLog'

const props = defineProps<{
  entries: TimelineEntry[]
  loading: boolean
  loadingMore?: boolean
  hasMore?: boolean
}>()

defineEmits<{
  'load-more': []
}>()

const FIELD_LABELS: Record<string, string> = {
  name: '名称', industry: '行业', phone: '电话', email: '邮箱',
  website: '网站', billing_street: '街道', billing_city: '城市',
  billing_state: '省份', billing_postal_code: '邮编', billing_country: '国家',
  description: '描述', first_name: '姓', last_name: '名', mobile: '手机',
  title: '职位', department: '部门', amount: '金额', stage_id: '销售阶段',
  close_date: '预计关闭日期', probability: '成功率', product_code: '产品编码',
  standard_price: '标准价格', cost: '成本', category: '分类', is_active: '是否启用',
  subject: '主题', type: '类型', status: '状态',
}

function fieldLabel(field: string): string {
  return FIELD_LABELS[field] || field
}

function formatTime(dateStr?: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  if (d.toDateString() === today.toDateString()) return '今天'
  if (d.toDateString() === yesterday.toDateString()) return '昨天'
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

function resultType(result: string): string {
  const map: Record<string, string> = { success: 'success', neutral: 'info', failure: 'danger', no_show: 'warning' }
  return map[result] || 'info'
}

function resultLabel(result: string): string {
  const map: Record<string, string> = { success: '成功', neutral: '一般', failure: '失败', no_show: '未到' }
  return map[result] || result
}

const groupedEntries = computed(() => {
  const groups: { date: string; entries: TimelineEntry[] }[] = []
  let currentDate = ''
  let currentGroup: TimelineEntry[] = []

  for (const entry of [...props.entries].sort((a, b) => {
    return new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime()
  })) {
    const date = formatDate(entry.created_at)
    if (date !== currentDate) {
      if (currentGroup.length > 0) {
        groups.push({ date: currentDate, entries: currentGroup })
      }
      currentDate = date
      currentGroup = [entry]
    } else {
      currentGroup.push(entry)
    }
  }
  if (currentGroup.length > 0) {
    groups.push({ date: currentDate, entries: currentGroup })
  }
  return groups
})
</script>

<style scoped>
.timeline { padding: 8px 0; }
.timeline-empty { padding: 40px 0; }
.timeline-list { position: relative; }
.timeline-date-header {
  font-size: 13px;
  font-weight: 600;
  color: #514f4d;
  padding: 12px 0 8px;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 8px;
}
.timeline-item {
  display: flex;
  gap: 10px;
  padding: 8px 0;
  position: relative;
}
.timeline-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}
.timeline-type-audit .timeline-dot { background: #e8f0fe; color: #1589ee; }
.timeline-type-event .timeline-dot { background: #e8f5e9; color: #67c23a; }
.timeline-type-task .timeline-dot { background: #fff3e0; color: #e6a23c; }
.timeline-content { flex: 1; min-width: 0; }
.timeline-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}
.timeline-user { font-size: 12px; font-weight: 600; color: #333; }
.timeline-time { font-size: 11px; color: #909399; }
.timeline-body { font-size: 13px; color: #606266; line-height: 1.5; }
.timeline-change {
  display: block;
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 3px;
  margin-top: 2px;
  word-break: break-all;
}
.timeline-tag { margin-left: 6px; }
.timeline-load-more { text-align: center; padding: 12px 0; }
</style>