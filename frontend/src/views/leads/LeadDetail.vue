<template>
  <div class="lead-detail-page" v-loading="loading">
    <div v-if="lead" class="detail-content">
      <div class="detail-header">
        <div>
          <h2>{{ lead.first_name }} {{ lead.last_name }}</h2>
          <div class="detail-meta">
            <el-tag :type="statusTag(lead.status)" size="small">{{ statusLabel(lead.status) }}</el-tag>
            <span class="meta-sep">|</span>
            <span>{{ lead.company }}</span>
            <span class="meta-sep">|</span>
            <span>{{ sourceLabel(lead.source) }}</span>
          </div>
        </div>
        <div class="header-actions">
          <el-button v-if="!lead.is_converted" size="small" type="success" @click="showConvertDialog">转化</el-button>
          <el-button size="small" @click="editLead">编辑</el-button>
        </div>
      </div>

      <!-- Converted Info -->
      <el-alert v-if="lead.is_converted" title="已转化" type="success" :closable="false" show-icon style="margin-bottom: 16px">
        <template #default>
          已转化为
          <router-link v-if="lead.converted_account_id" :to="`/accounts/${lead.converted_account_id}`" class="alert-link">账户</router-link>
          <router-link v-if="lead.converted_contact_id" :to="`/contacts/${lead.converted_contact_id}`" class="alert-link">联系人</router-link>
          <router-link v-if="lead.converted_opportunity_id" :to="`/opportunities/${lead.converted_opportunity_id}`" class="alert-link">商机</router-link>
        </template>
      </el-alert>

      <el-descriptions :column="2" border size="small">
        <el-descriptions-item label="姓名">{{ lead.first_name }} {{ lead.last_name }}</el-descriptions-item>
        <el-descriptions-item label="公司">{{ lead.company }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ lead.email || '-' }}</el-descriptions-item>
        <el-descriptions-item label="电话">{{ lead.phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="手机">{{ lead.mobile_phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="职位">{{ lead.title || '-' }}</el-descriptions-item>
        <el-descriptions-item label="行业">{{ lead.industry || '-' }}</el-descriptions-item>
        <el-descriptions-item label="来源">{{ sourceLabel(lead.source) }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(lead.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatDate(lead.updated_at) }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ lead.description || '无' }}</el-descriptions-item>
      </el-descriptions>

      <!-- Convert Dialog -->
      <el-dialog v-model="convertDialog.visible" title="转化线索" width="500px" :close-on-click-modal="false">
        <el-form :model="convertForm" label-width="140px" size="small">
          <el-form-item label="目标账户">
            <el-radio-group v-model="convertForm.account_mode">
              <el-radio value="new">创建新账户</el-radio>
              <el-radio value="existing">使用已有账户</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item v-if="convertForm.account_mode === 'new'" label="账户名称">
            <el-input v-model="convertForm.account_name" :placeholder="`默认：${lead.company}`" />
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
            <el-input v-model="convertForm.opportunity_name" :placeholder="`默认：${lead.company}`" />
          </el-form-item>
          <el-form-item v-if="convertForm.create_opportunity" label="金额">
            <el-input-number v-model="convertForm.opportunity_amount" :min="0" style="width: 100%" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button size="small" @click="convertDialog.visible = false">取消</el-button>
          <el-button size="small" type="primary" @click="handleConvert">确认转化</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

interface Lead {
  id: string
  first_name: string
  last_name: string
  company: string
  email: string | null
  phone: string | null
  mobile_phone: string | null
  title: string | null
  industry: string | null
  status: string
  source: string
  description: string | null
  is_converted: boolean
  converted_account_id: string | null
  converted_contact_id: string | null
  converted_opportunity_id: string | null
  created_at: string
  updated_at: string
}

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const lead = ref<Lead | null>(null)
const accountOptions = ref<{ id: string; name: string }[]>([])

const convertDialog = reactive({ visible: false })
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
function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}
function editLead() { router.push(`/leads/${lead.value!.id}/edit`) }

async function loadLead() {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/leads/${route.params.id}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('Failed to load')
    lead.value = await res.json()
  } catch (e: any) {
    ElMessage.error('加载失败: ' + (e.message || ''))
  } finally {
    loading.value = false
  }
}

async function showConvertDialog() {
  if (!lead.value) return
  convertForm.account_mode = 'new'
  convertForm.account_name = lead.value.company
  convertForm.account_id = ''
  convertForm.create_opportunity = true
  convertForm.opportunity_name = `${lead.value.company} - ${lead.value.first_name} ${lead.value.last_name}`
  convertForm.opportunity_amount = 0
  convertDialog.visible = true

  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch('/api/accounts?page_size=100', {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (res.ok) {
      const data = await res.json()
      accountOptions.value = (data.items || []).map((a: any) => ({ id: a.id, name: a.name }))
    }
  } catch { /* ignore */ }
}

async function handleConvert() {
  try {
    const token = localStorage.getItem('access_token')
    const body: any = { create_opportunity: convertForm.create_opportunity }
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

    const res = await fetch(`/api/leads/${lead.value!.id}/convert`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(body),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Convert failed')
    }
    ElMessage.success('线索已转化')
    convertDialog.visible = false
    await loadLead()
  } catch (e: any) {
    ElMessage.error('转化失败: ' + (e.message || ''))
  }
}

onMounted(loadLead)
</script>

<style scoped>
.lead-detail-page {
  background: #fff;
  border: 1px solid #dddbda;
  border-radius: 3px;
  padding: 20px;
}
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}
.detail-header h2 { margin: 0 0 6px; font-size: 20px; font-weight: 700; color: #080707; }
.detail-meta { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #706e6b; }
.meta-sep { color: #dddbda; }
.alert-link { color: #67c23a; text-decoration: underline; margin-left: 4px; }
</style>