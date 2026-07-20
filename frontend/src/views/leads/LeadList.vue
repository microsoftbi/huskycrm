<template>
  <div class="lead-list-page">
    <div class="page-header">
      <h2>线索管理</h2>
      <el-button type="primary" size="small" icon="plus" @click="createNew">新建线索</el-button>
    </div>

    <!-- Filters -->
    <div class="filters">
      <el-input
        v-model="search"
        placeholder="搜索名称/公司/邮箱..."
        size="small"
        clearable
        style="width: 240px"
        @clear="loadData"
        @keyup.enter="loadData"
      />
      <el-select v-model="statusFilter" placeholder="状态" clearable size="small" style="width: 140px" @change="loadData">
        <el-option label="全部" value="" />
        <el-option label="新线索" value="New" />
        <el-option label="已联系" value="Contacted" />
        <el-option label="已合格" value="Qualified" />
        <el-option label="不合格" value="Unqualified" />
        <el-option label="已转化" value="Converted" />
      </el-select>
      <el-select v-model="sourceFilter" placeholder="来源" clearable size="small" style="width: 140px" @change="loadData">
        <el-option label="全部" value="" />
        <el-option label="网站" value="Web" />
        <el-option label="电话" value="Phone" />
        <el-option label="推荐" value="Referral" />
        <el-option label="会议" value="Conference" />
        <el-option label="邮件" value="Email" />
        <el-option label="其他" value="Other" />
      </el-select>
      <el-button size="small" type="primary" @click="loadData">搜索</el-button>
    </div>

    <!-- Table -->
    <el-table :data="items" v-loading="loading" stripe style="width: 100%">
      <el-table-column label="姓名" min-width="160">
        <template #default="{ row }">
          <router-link :to="`/leads/${row.id}`" class="record-link">
            {{ row.first_name }} {{ row.last_name }}
          </router-link>
        </template>
      </el-table-column>
      <el-table-column prop="company" label="公司" min-width="160" />
      <el-table-column prop="email" label="邮箱" min-width="180" />
      <el-table-column prop="phone" label="电话" width="130" />
      <el-table-column prop="status" label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="statusTag(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="source" label="来源" width="90">
        <template #default="{ row }">
          <el-tag size="small" effect="plain">{{ sourceLabel(row.source) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="owner_id" label="负责人" width="120">
        <template #default="{ row }">
          {{ row.owner?.display_name || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button v-if="!row.is_converted" size="small" type="success" link @click="convertLead(row)">转化</el-button>
          <el-button size="small" type="primary" link @click="editLead(row)">编辑</el-button>
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

    <!-- Convert Dialog -->
    <el-dialog v-model="convertDialog.visible" title="转化线索" width="500px" :close-on-click-modal="false">
      <el-form :model="convertForm" label-width="140px" size="small">
        <el-form-item label="目标账户">
          <el-radio-group v-model="convertForm.account_mode">
            <el-radio value="new">创建新账户</el-radio>
            <el-radio value="existing">使用已有账户</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="convertForm.account_mode === 'new'" label="账户名称" required>
          <el-input v-model="convertForm.account_name" :placeholder="`默认：${convertLeadData?.company || ''}`" />
        </el-form-item>
        <el-form-item v-if="convertForm.account_mode === 'existing'" label="选择账户" required>
          <el-select v-model="convertForm.account_id" filterable placeholder="搜索账户..." style="width: 100%">
            <el-option v-for="a in accountOptions" :key="a.id" :label="a.name" :value="a.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="创建商机">
          <el-switch v-model="convertForm.create_opportunity" />
        </el-form-item>
        <el-form-item v-if="convertForm.create_opportunity" label="商机名称">
          <el-input v-model="convertForm.opportunity_name" :placeholder="`默认：${convertLeadData?.company || ''}`" />
        </el-form-item>
        <el-form-item v-if="convertForm.create_opportunity" label="商机金额">
          <el-input-number v-model="convertForm.opportunity_amount" :min="0" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button size="small" @click="convertDialog.visible = false">取消</el-button>
        <el-button size="small" type="primary" @click="handleConvert">确认转化</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

interface Lead {
  id: string
  first_name: string
  last_name: string
  company: string
  email: string | null
  phone: string | null
  status: string
  source: string
  is_converted: boolean
  owner: { display_name: string } | null
  created_at: string
}

const router = useRouter()
const loading = ref(false)
const items = ref<Lead[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const search = ref('')
const statusFilter = ref('')
const sourceFilter = ref('')
const accountOptions = ref<{ id: string; name: string }[]>([])
const convertLeadData = ref<Lead | null>(null)

const convertDialog = reactive({
  visible: false,
  leadId: '',
})

const convertForm = reactive({
  account_mode: 'new' as 'new' | 'existing',
  account_name: '',
  account_id: '',
  create_opportunity: true,
  opportunity_name: '',
  opportunity_amount: 0,
})

function statusLabel(status: string): string {
  const labels: Record<string, string> = { New: '新线索', Contacted: '已联系', Qualified: '已合格', Unqualified: '不合格', Converted: '已转化' }
  return labels[status] || status
}

function statusTag(status: string): string {
  const tags: Record<string, string> = { New: 'info', Contacted: 'primary', Qualified: 'warning', Unqualified: 'danger', Converted: 'success' }
  return tags[status] || ''
}

function sourceLabel(source: string): string {
  const labels: Record<string, string> = { Web: '网站', Phone: '电话', Referral: '推荐', Conference: '会议', Email: '邮件', Other: '其他' }
  return labels[source] || source
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
    if (sourceFilter.value) params.set('source_filter', sourceFilter.value)

    const res = await fetch(`/api/leads?${params}`, {
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
  router.push('/leads/new')
}

function editLead(row: Lead) {
  router.push(`/leads/${row.id}/edit`)
}

async function handleDelete(row: Lead) {
  try {
    await ElMessageBox.confirm(`确定删除线索「${row.first_name} ${row.last_name}」吗？`, '确认删除', {
      confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning',
    })
  } catch { return }

  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/leads/${row.id}`, {
      method: 'DELETE', headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('Delete failed')
    ElMessage.success('已删除')
    await loadData()
  } catch (e: any) {
    ElMessage.error('删除失败: ' + (e.message || ''))
  }
}

function convertLead(row: Lead) {
  convertLeadData.value = row
  convertDialog.leadId = row.id
  convertForm.account_mode = 'new'
  convertForm.account_name = row.company
  convertForm.account_id = ''
  convertForm.create_opportunity = true
  convertForm.opportunity_name = `${row.company} - ${row.first_name} ${row.last_name}`
  convertForm.opportunity_amount = 0
  convertDialog.visible = true
  loadAccounts()
}

async function loadAccounts() {
  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch('/api/accounts?page_size=100', {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) return
    const data = await res.json()
    accountOptions.value = (data.items || []).map((a: any) => ({ id: a.id, name: a.name }))
  } catch { /* ignore */ }
}

async function handleConvert() {
  try {
    const token = localStorage.getItem('access_token')
    const body: any = {
      create_opportunity: convertForm.create_opportunity,
    }
    if (convertForm.account_mode === 'new') {
      body.create_account = true
      body.account_name = convertForm.account_name || undefined
    } else {
      body.create_account = false
      body.account_id = convertForm.account_id
    }
    if (convertForm.create_opportunity) {
      body.opportunity_name = convertForm.opportunity_name || undefined
      body.opportunity_amount = convertForm.opportunity_amount || undefined
    }

    const res = await fetch(`/api/leads/${convertDialog.leadId}/convert`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(body),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Convert failed')
    }
    const data = await res.json()
    ElMessage.success('线索已转化')
    convertDialog.visible = false
    await loadData()
  } catch (e: any) {
    ElMessage.error('转化失败: ' + (e.message || ''))
  }
}

onMounted(loadData)
</script>

<style scoped>
.lead-list-page {
  background: #fff;
  border: 1px solid #dddbda;
  border-radius: 3px;
  padding: 20px;
}
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h2 { margin: 0; font-size: 18px; font-weight: 700; color: #080707; }
.filters { display: flex; gap: 8px; margin-bottom: 16px; align-items: center; }
.record-link { color: #1589ee; text-decoration: none; font-weight: 500; }
.record-link:hover { text-decoration: underline; }
.pagination-wrapper { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>