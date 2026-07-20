<template>
  <div class="recycle-bin-page">
    <div class="page-header">
      <h2>回收站</h2>
      <div class="header-actions">
        <el-button size="small" type="danger" plain @click="handleCleanup">清理过期记录</el-button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters">
      <el-select
        v-model="filter.object_type"
        placeholder="对象类型"
        clearable
        size="small"
        style="width: 160px"
        @change="loadData"
      >
        <el-option label="全部" value="" />
        <el-option label="账户" value="account" />
        <el-option label="联系人" value="contact" />
        <el-option label="销售机会" value="opportunity" />
        <el-option label="产品" value="product" />
        <el-option label="拜访" value="event" />
        <el-option label="任务" value="task" />
      </el-select>
      <el-input
        v-model="filter.search"
        placeholder="搜索名称..."
        size="small"
        clearable
        style="width: 200px"
        @clear="loadData"
        @keyup.enter="loadData"
      />
      <el-button size="small" type="primary" @click="loadData">搜索</el-button>
    </div>

    <!-- Table -->
    <el-table
      :data="items"
      v-loading="loading"
      stripe
      style="width: 100%"
      @selection-change="onSelectionChange"
    >
      <el-table-column type="selection" width="40" />
      <el-table-column prop="object_name" label="名称" min-width="200" />
      <el-table-column prop="object_type" label="类型" width="120">
        <template #default="{ row }">
          <el-tag :type="typeTag(row.object_type)" size="small">
            {{ typeLabel(row.object_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="deleted_at" label="删除时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.deleted_at) }}
        </template>
      </el-table-column>
      <el-table-column prop="days_remaining" label="剩余天数" width="120">
        <template #default="{ row }">
          <el-tag :type="daysTag(row.days_remaining)" size="small">
            {{ row.days_remaining }} 天
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="handleRestore(row)">
            恢复
          </el-button>
          <el-button size="small" type="danger" link @click="handlePermanentDelete(row)">
            彻底删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Pagination -->
    <div class="pagination-wrapper">
      <div class="batch-actions">
        <el-button
          size="small"
          type="primary"
          :disabled="selectedIds.length === 0"
          @click="handleBatchRestore"
        >
          批量恢复 ({{ selectedIds.length }})
        </el-button>
        <el-button
          size="small"
          type="danger"
          :disabled="selectedIds.length === 0"
          @click="handleBatchDelete"
        >
          批量彻底删除 ({{ selectedIds.length }})
        </el-button>
      </div>
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadData"
      />
    </div>

    <!-- Restore success dialog -->
    <el-dialog v-model="resultDialog.visible" title="操作结果" width="400px">
      <p>{{ resultDialog.message }}</p>
      <template #footer>
        <el-button @click="resultDialog.visible = false">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface RecycleBinItem {
  id: string
  object_type: string
  object_name: string
  deleted_by: string | null
  deleted_at: string
  days_remaining: number
}

const loading = ref(false)
const items = ref<RecycleBinItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const selectedIds = ref<string[]>([])

const filter = reactive({
  object_type: '',
  search: '',
})

const resultDialog = reactive({
  visible: false,
  message: '',
})

const TYPE_LABELS: Record<string, string> = {
  account: '账户',
  contact: '联系人',
  opportunity: '销售机会',
  product: '产品',
  event: '拜访',
  task: '任务',
}

const TYPE_TAGS: Record<string, string> = {
  account: '',
  contact: 'success',
  opportunity: 'warning',
  product: 'info',
  event: '',
  task: 'info',
}

function typeLabel(type: string): string {
  return TYPE_LABELS[type] || type
}

function typeTag(type: string): string {
  return TYPE_TAGS[type] || ''
}

function daysTag(days: number): string {
  if (days <= 7) return 'danger'
  if (days <= 14) return 'warning'
  return 'success'
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
    if (filter.object_type) params.set('object_type', filter.object_type)
    if (filter.search) params.set('search', filter.search)

    const res = await fetch(`/api/recycle-bin?${params}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('Failed to load')
    const data = await res.json()
    items.value = data.items || []
    total.value = data.total || 0
  } catch (e: any) {
    ElMessage.error('加载回收站数据失败: ' + (e.message || ''))
  } finally {
    loading.value = false
  }
}

function onSelectionChange(selection: RecycleBinItem[]) {
  selectedIds.value = selection.map((s) => s.id)
}

async function handleRestore(row: RecycleBinItem) {
  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/recycle-bin/${row.object_type}/${row.id}/restore`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('Restore failed')
    ElMessage.success(`已恢复「${row.object_name}」`)
    await loadData()
  } catch (e: any) {
    ElMessage.error('恢复失败: ' + (e.message || ''))
  }
}

async function handlePermanentDelete(row: RecycleBinItem) {
  try {
    await ElMessageBox.confirm(
      `确定要彻底删除「${row.object_name}」吗？此操作不可撤销。`,
      '确认删除',
      { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }

  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/recycle-bin/${row.object_type}/${row.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('Delete failed')
    ElMessage.success('已彻底删除')
    await loadData()
  } catch (e: any) {
    ElMessage.error('删除失败: ' + (e.message || ''))
  }
}

async function handleBatchRestore() {
  const selectedItems = items.value.filter((i) => selectedIds.value.includes(i.id))
  let success = 0
  for (const item of selectedItems) {
    try {
      const token = localStorage.getItem('access_token')
      const res = await fetch(`/api/recycle-bin/${item.object_type}/${item.id}/restore`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) success++
    } catch {
      // continue
    }
  }
  ElMessage.success(`已恢复 ${success} 条记录`)
  await loadData()
}

async function handleBatchDelete() {
  try {
    await ElMessageBox.confirm(
      `确定要彻底删除选中的 ${selectedIds.value.length} 条记录吗？此操作不可撤销。`,
      '确认批量删除',
      { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }

  const selectedItems = items.value.filter((i) => selectedIds.value.includes(i.id))
  let success = 0
  for (const item of selectedItems) {
    try {
      const token = localStorage.getItem('access_token')
      const res = await fetch(`/api/recycle-bin/${item.object_type}/${item.id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) success++
    } catch {
      // continue
    }
  }
  ElMessage.success(`已彻底删除 ${success} 条记录`)
  await loadData()
}

async function handleCleanup() {
  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch('/api/recycle-bin/cleanup', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('Cleanup failed')
    const data = await res.json()
    ElMessage.success(data.message || '清理完成')
    await loadData()
  } catch (e: any) {
    ElMessage.error('清理失败: ' + (e.message || ''))
  }
}

onMounted(loadData)
</script>

<style scoped>
.recycle-bin-page {
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

.pagination-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
}

.batch-actions {
  display: flex;
  gap: 8px;
}
</style>