<template>
  <div class="event-detail" v-loading="loading">
    <div class="sf-page-header">
      <h2 class="sf-page-title">拜访详情</h2>
    </div>

    <template v-if="event">
      <RecordHeader
        :title="event.subject"
        icon-name="phone"
        :hide-edit="!can('edit')"
        :hide-delete="!canDelete"
        @edit="$router.push(`/events/${event.id}/edit`)"
        @delete="handleDelete"
      />

      <HighlightsPanel :items="highlightItems" />

      <RecordTabs :tabs="tabs">
        <!-- Details Tab -->
        <template #panel-details>
          <RecordSection title="拜访信息" :fields="eventFields" />
          <RecordSection title="拜访内容" :fields="contentFields" />
          <RecordSection title="系统信息" :fields="systemFields" />
        </template>

        <!-- Check-in/Check-out Tab -->
        <template #panel-checkin>
          <div class="sf-card">
            <div class="sf-card-header">
              <h3 class="sf-card-title">签到/签退</h3>
            </div>
            <div class="sf-card-body">
              <el-descriptions :column="2" border size="small">
                <el-descriptions-item label="状态">
                  <el-tag :type="statusTagType" size="small">{{ statusLabel }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="签到位置">{{ event.location || '-' }}</el-descriptions-item>
                <el-descriptions-item label="实际开始时间">{{ event.actual_start_time || '-' }}</el-descriptions-item>
                <el-descriptions-item label="实际结束时间">{{ event.actual_end_time || '-' }}</el-descriptions-item>
                <el-descriptions-item label="实际时长">
                  {{ event.duration_minutes ? `${event.duration_minutes} 分钟` : '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="拜访结果">{{ outcomeLabel }}</el-descriptions-item>
              </el-descriptions>

              <div style="margin-top: 16px; display: flex; gap: 12px;">
                <el-button v-if="event.status === 'planned'" type="success" :loading="checkingIn"
                  @click="handleCheckIn">
                  <el-icon><circle-check /></el-icon> 签到
                </el-button>
                <el-button v-if="event.status === 'in_progress'" type="warning" :loading="checkingOut"
                  @click="showCheckOutDialog = true">
                  <el-icon><circle-close /></el-icon> 签退
                </el-button>
                <el-button v-if="event.status === 'planned' || event.status === 'in_progress'"
                  type="danger" plain @click="handleCancel">取消拜访</el-button>
              </div>
            </div>
          </div>
        </template>

        <!-- Tasks Tab -->
        <template #panel-tasks>
          <div class="sf-card">
            <div class="sf-card-header">
              <h3 class="sf-card-title">任务清单</h3>
              <el-button type="primary" size="small" @click="showTaskDialog = true">
                <el-icon><plus /></el-icon> 添加任务
              </el-button>
            </div>
            <div class="sf-card-body" style="padding:0;">
              <el-table :data="tasks" stripe size="small" style="width:100%" empty-text="暂无任务">
                <el-table-column label="任务" min-width="250">
                  <template #default="{ row }">
                    <span :class="{ 'task-completed': row.status === 'completed' }">
                      {{ row.subject }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column label="状态" width="150">
                  <template #default="{ row }">
                    <el-select :model-value="row.status" size="small" @change="(val: string) => updateTaskStatus(row, val)">
                      <el-option label="未开始" value="not_started" />
                      <el-option label="进行中" value="in_progress" />
                      <el-option label="已完成" value="completed" />
                      <el-option label="推迟" value="deferred" />
                    </el-select>
                  </template>
                </el-table-column>
                <el-table-column label="优先级" width="100">
                  <template #default="{ row }">
                    <el-tag :type="priorityTagType(row.priority)" size="small">{{ priorityLabel(row.priority) }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="截止日期" width="140">
                  <template #default="{ row }">{{ row.activity_date || '-' }}</template>
                </el-table-column>
                <el-table-column label="操作" width="80" fixed="right">
                  <template #default="{ row }">
                    <el-button type="danger" link size="small" @click="handleDeleteTask(row)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </template>
      </RecordTabs>
    </template>

    <!-- Check-out Dialog -->
    <el-dialog v-model="showCheckOutDialog" title="签退" width="500px">
      <el-form label-position="top" size="small">
        <el-form-item label="拜访纪要">
          <el-input v-model="checkOutForm.description" type="textarea" :rows="3" placeholder="请记录拜访纪要" />
        </el-form-item>
        <el-form-item label="拜访结果">
          <el-select v-model="checkOutForm.outcome" style="width:100%">
            <el-option label="成功" value="success" />
            <el-option label="一般" value="neutral" />
            <el-option label="失败" value="failure" />
            <el-option label="未出席" value="no_show" />
          </el-select>
        </el-form-item>
        <el-form-item label="下一步计划">
          <el-input v-model="checkOutForm.next_steps" type="textarea" :rows="2" placeholder="请记录下一步计划" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCheckOutDialog = false">取消</el-button>
        <el-button type="primary" :loading="checkingOut" @click="handleCheckOut">确定签退</el-button>
      </template>
    </el-dialog>

    <!-- Add Task Dialog -->
    <el-dialog v-model="showTaskDialog" title="添加任务" width="450px">
      <el-form ref="taskFormRef" :model="taskForm" :rules="taskRules" label-position="top" size="small">
        <el-form-item label="任务主题" prop="subject">
          <el-input v-model="taskForm.subject" placeholder="请输入任务主题" />
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="优先级">
              <el-select v-model="taskForm.priority" style="width:100%">
                <el-option label="高" value="high" />
                <el-option label="普通" value="normal" />
                <el-option label="低" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="截止日期">
              <el-date-picker v-model="taskForm.activity_date" type="date" placeholder="选择日期" style="width:100%"
                value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="任务描述">
          <el-input v-model="taskForm.description" type="textarea" :rows="2" placeholder="任务描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTaskDialog = false">取消</el-button>
        <el-button type="primary" :loading="taskSaving" @click="handleAddTask">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { eventsApi } from '../../api/events'
import { usePermissions } from '../../composables/usePermissions'
import type { Event, Task, TaskCreate } from '../../types/event'
import RecordHeader from '../../components/record/RecordHeader.vue'
import RecordSection from '../../components/record/RecordSection.vue'
import HighlightsPanel from '../../components/record/HighlightsPanel.vue'
import RecordTabs from '../../components/record/RecordTabs.vue'

const route = useRoute()
const router = useRouter()
const { can, canDelete } = usePermissions()
const event = ref<Event | null>(null)
const loading = ref(false)
const tasks = ref<Task[]>([])

// Check-in/out
const checkingIn = ref(false)
const checkingOut = ref(false)
const showCheckOutDialog = ref(false)
const checkOutForm = ref({ description: '', outcome: 'success', next_steps: '' })

// Task dialog
const showTaskDialog = ref(false)
const taskSaving = ref(false)
const taskFormRef = ref()
const taskForm = ref<TaskCreate>({ subject: '', priority: 'normal', activity_date: '', description: '' })
const taskRules = { subject: [{ required: true, message: '请输入任务主题', trigger: 'blur' }] }

const highlightItems = computed(() => [
  { label: '类型', value: typeLabel, flex: '1' },
  { label: '状态', value: statusLabel, flex: '1' },
  { label: '计划时间', value: event.value?.start_datetime?.replace('T', ' ')?.substring(0, 16) || '-', flex: '1.5' },
  { label: '关联账户', value: event.value?.what_type === 'account' ? `#${event.value.what_id}` : '-', flex: '1' },
  { label: '关联联系人', value: event.value?.who_id ? `#${event.value.who_id}` : '-', flex: '1' },
])

const typeLabel = computed(() => {
  const labels: Record<string, string> = {
    'Visit': '上门拜访', 'Phone Call': '电话拜访',
    'Video Conference': '视频会议', 'Client Visit': '客户来访', 'Other': '其他',
  }
  return event.value ? (labels[event.value.type] || event.value.type) : '-'
})

const statusLabel = computed(() => {
  const labels: Record<string, string> = {
    'planned': '计划中', 'in_progress': '进行中',
    'completed': '已完成', 'cancelled': '已取消',
  }
  return event.value ? (labels[event.value.status] || event.value.status) : '-'
})

const statusTagType = computed(() => {
  const types: Record<string, string> = {
    'planned': 'info', 'in_progress': 'warning',
    'completed': 'success', 'cancelled': 'danger',
  }
  return event.value ? (types[event.value.status] || 'info') : 'info'
})

const outcomeLabel = computed(() => {
  const labels: Record<string, string> = {
    'success': '成功', 'neutral': '一般', 'failure': '失败', 'no_show': '未出席',
  }
  return event.value?.outcome ? (labels[event.value.outcome] || event.value.outcome) : '-'
})

const tabs = computed(() => [
  { key: 'details', label: '详细信息' },
  { key: 'checkin', label: '签到信息' },
  { key: 'tasks', label: `任务清单${tasks.value.length ? ` (${tasks.value.length})` : ''}` },
])

const eventFields = computed(() => [
  { label: '主题', value: event.value?.subject },
  { label: '类型', value: typeLabel.value },
  { label: '状态', value: statusLabel.value },
  { label: '计划开始', value: event.value?.start_datetime?.replace('T', ' ')?.substring(0, 16) },
  { label: '计划结束', value: event.value?.end_datetime?.replace('T', ' ')?.substring(0, 16) },
  { label: '忙/闲', value: event.value?.show_as === 'busy' ? '忙碌' : event.value?.show_as === 'free' ? '空闲' : '外出' },
  { label: '关联账户', value: event.value?.what_type === 'account' ? `#${event.value.what_id}` : '-' },
  { label: '关联联系人', value: event.value?.who_id ? `#${event.value.who_id}` : '-' },
  { label: '关联商机', value: event.value?.what_type === 'opportunity' ? `#${event.value.what_id}` : '-' },
])

const contentFields = computed(() => [
  { label: '拜访目的', value: event.value?.purpose },
  { label: '拜访准备', value: event.value?.preparation_notes },
  { label: '拜访纪要', value: event.value?.description },
  { label: '拜访结果', value: outcomeLabel.value },
  { label: '下一步计划', value: event.value?.next_steps },
])

const systemFields = computed(() => [
  { label: '创建时间', value: event.value?.created_at },
  { label: '更新时间', value: event.value?.updated_at },
])

function priorityLabel(p: string) {
  const labels: Record<string, string> = { 'high': '高', 'normal': '普通', 'low': '低' }
  return labels[p] || p
}

function priorityTagType(p: string) {
  const types: Record<string, string> = { 'high': 'danger', 'normal': 'info', 'low': 'default' }
  return types[p] || 'info'
}

async function fetchEvent() {
  loading.value = true
  try {
    const { data } = await eventsApi.get(route.params.id as string)
    event.value = data
    tasks.value = data.tasks || []
  } catch {
    ElMessage.error('拜访记录不存在')
    router.push('/events')
  } finally {
    loading.value = false
  }
}

async function handleCheckIn() {
  if (!event.value) return
  checkingIn.value = true
  try {
    const { data } = await eventsApi.checkIn(event.value.id)
    event.value = data
    ElMessage.success('签到成功')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '签到失败')
  } finally {
    checkingIn.value = false
  }
}

async function handleCheckOut() {
  if (!event.value) return
  checkingOut.value = true
  try {
    const { data } = await eventsApi.checkOut(event.value.id, checkOutForm.value)
    event.value = data
    showCheckOutDialog.value = false
    checkOutForm.value = { description: '', outcome: 'success', next_steps: '' }
    ElMessage.success('签退成功')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '签退失败')
  } finally {
    checkingOut.value = false
  }
}

async function handleCancel() {
  if (!event.value) return
  try {
    await ElMessageBox.confirm('确定取消该拜访吗？', '确认', { type: 'warning' })
    await eventsApi.update(event.value.id, { status: 'cancelled' })
    event.value!.status = 'cancelled'
    ElMessage.success('已取消')
  } catch { /* cancelled */ }
}

async function handleDelete() {
  if (!event.value) return
  try {
    await ElMessageBox.confirm(`确定删除拜访 "${event.value.subject}" 吗？`, '确认删除', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
    await eventsApi.delete(event.value.id)
    ElMessage.success('删除成功')
    router.push('/events')
  } catch { /* cancelled */ }
}

async function handleAddTask() {
  if (!event.value) return
  const valid = await taskFormRef.value.validate().catch(() => false)
  if (!valid) return
  taskSaving.value = true
  try {
    const { data } = await eventsApi.createTask(event.value.id, taskForm.value)
    tasks.value.push(data)
    showTaskDialog.value = false
    taskForm.value = { subject: '', priority: 'normal', activity_date: '', description: '' }
    ElMessage.success('任务已添加')
  } catch {
    ElMessage.error('添加失败')
  } finally {
    taskSaving.value = false
  }
}

async function updateTaskStatus(task: Task, newStatus: string) {
  if (!event.value) return
  try {
    await eventsApi.updateTask(event.value.id, task.id, { status: newStatus })
    task.status = newStatus
  } catch {
    ElMessage.error('更新失败')
  }
}

async function handleDeleteTask(task: Task) {
  if (!event.value) return
  try {
    await ElMessageBox.confirm('确定删除该任务吗？', '确认', { type: 'warning' })
    await eventsApi.deleteTask(event.value.id, task.id)
    tasks.value = tasks.value.filter(t => t.id !== task.id)
    ElMessage.success('已删除')
  } catch { /* cancelled */ }
}

onMounted(fetchEvent)
</script>

<style scoped>
.event-detail { max-width: 960px; }
.task-completed { text-decoration: line-through; color: #706e6b; }
</style>
