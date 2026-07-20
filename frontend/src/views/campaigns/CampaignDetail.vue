<template>
  <div class="campaign-detail-page" v-loading="loading">
    <div v-if="campaign" class="detail-content">
      <!-- Header -->
      <div class="detail-header">
        <div>
          <h2>{{ campaign.name }}</h2>
          <div class="detail-meta">
            <el-tag :type="statusTag(campaign.status)" size="small">{{ statusLabel(campaign.status) }}</el-tag>
            <span class="meta-sep">|</span>
            <span>{{ typeLabel(campaign.type) }}</span>
          </div>
        </div>
        <div class="header-actions">
          <el-button size="small" @click="editCampaign">编辑</el-button>
        </div>
      </div>

      <el-tabs v-model="activeTab">
        <!-- Overview Tab -->
        <el-tab-pane label="概览" name="overview">
          <div class="overview-grid">
            <div class="info-section">
              <h3>基本信息</h3>
              <el-descriptions :column="2" size="small" border>
                <el-descriptions-item label="预算">
                  {{ campaign.budget ? '¥' + formatNumber(campaign.budget) : '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="实际成本">
                  {{ campaign.actual_cost ? '¥' + formatNumber(campaign.actual_cost) : '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="开始日期">
                  {{ campaign.start_date || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="结束日期">
                  {{ campaign.end_date || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="描述" :span="2">
                  {{ campaign.description || '无' }}
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <!-- ROI Card -->
            <div class="roi-section">
              <h3>ROI 分析</h3>
              <div class="roi-card">
                <div class="roi-metric">
                  <span class="roi-label">成员数</span>
                  <span class="roi-value">{{ roiData.member_count }}</span>
                </div>
                <div class="roi-metric">
                  <span class="roi-label">转化商机</span>
                  <span class="roi-value">{{ roiData.converted_opportunities }}</span>
                </div>
                <div class="roi-metric">
                  <span class="roi-label">商机总额</span>
                  <span class="roi-value">¥{{ formatNumber(roiData.converted_amount) }}</span>
                </div>
                <div class="roi-metric">
                  <span class="roi-label">ROI</span>
                  <span class="roi-value" :class="roiClass(roiData.roi)">
                    {{ roiData.roi !== null ? roiData.roi + '%' : 'N/A' }}
                  </span>
                </div>
                <div class="roi-metric">
                  <span class="roi-label">评级</span>
                  <span class="roi-value" :class="roiClass(roiData.roi)">{{ roiData.roi_label }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- Members Tab -->
        <el-tab-pane label="活动成员" name="members">
          <div class="members-section">
            <div class="section-header">
              <h3>成员列表</h3>
              <el-button size="small" type="primary" @click="showAddMember = true">添加成员</el-button>
            </div>

            <el-table :data="members" stripe style="width: 100%" size="small">
              <el-table-column prop="contact_name" label="联系人" min-width="160" />
              <el-table-column prop="contact_email" label="邮箱" min-width="200" />
              <el-table-column prop="status" label="状态" width="120">
                <template #default="{ row }">
                  <el-select
                    v-model="row.status"
                    size="small"
                    @change="(val: string) => updateMemberStatus(row, val)"
                  >
                    <el-option label="已邀请" value="invited" />
                    <el-option label="已参加" value="attended" />
                    <el-option label="已转化" value="converted" />
                    <el-option label="无兴趣" value="not_interested" />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column label="添加时间" width="160">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80">
                <template #default="{ row }">
                  <el-button size="small" type="danger" link @click="removeMember(row)">移除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>

      <!-- Add Member Dialog -->
      <el-dialog v-model="showAddMember" title="添加成员" width="400px">
        <el-form size="small">
          <el-form-item label="联系人" required>
            <el-select
              v-model="newMember.contact_id"
              filterable
              remote
              :remote-method="searchContacts"
              placeholder="搜索联系人"
              style="width: 100%"
            >
              <el-option
                v-for="c in contactOptions"
                :key="c.id"
                :label="c.name"
                :value="c.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="newMember.status" style="width: 100%">
              <el-option label="已邀请" value="invited" />
              <el-option label="已参加" value="attended" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button size="small" @click="showAddMember = false">取消</el-button>
          <el-button size="small" type="primary" @click="addMember">添加</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

interface CampaignMember {
  id: string
  contact_id: string | null
  contact_name: string | null
  contact_email: string | null
  status: string
  created_at: string
}

interface Campaign {
  id: string
  name: string
  type: string
  status: string
  budget: number | null
  actual_cost: number | null
  start_date: string | null
  end_date: string | null
  description: string | null
  member_count: number
  converted_opportunities: number
  converted_amount: number
  roi: number | null
  created_at: string
  updated_at: string
  members: CampaignMember[]
}

interface ROIData {
  budget: number | null
  actual_cost: number | null
  member_count: number
  converted_opportunities: number
  converted_amount: number
  roi: number | null
  roi_label: string
}

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const campaign = ref<Campaign | null>(null)
const members = ref<CampaignMember[]>([])
const roiData = reactive<ROIData>({
  budget: null,
  actual_cost: null,
  member_count: 0,
  converted_opportunities: 0,
  converted_amount: 0,
  roi: null,
  roi_label: 'N/A',
})
const activeTab = ref('overview')
const showAddMember = ref(false)
const newMember = reactive({ contact_id: '', status: 'invited' })
const contactOptions = ref<{ id: string; name: string }[]>([])

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

function roiClass(roi: number | null): string {
  if (roi === null) return ''
  if (roi > 500) return 'roi-excellent'
  if (roi > 200) return 'roi-good'
  if (roi > 0) return 'roi-normal'
  return 'roi-bad'
}

function formatNumber(n: number): string {
  return n.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

async function loadCampaign() {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const id = route.params.id
    const res = await fetch(`/api/campaigns/${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('Failed to load')
    campaign.value = await res.json()
    members.value = campaign.value.members || []

    // Load ROI
    const roiRes = await fetch(`/api/campaigns/${id}/roi`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (roiRes.ok) {
      const data = await roiRes.json()
      Object.assign(roiData, data)
    }
  } catch (e: any) {
    ElMessage.error('加载失败: ' + (e.message || ''))
  } finally {
    loading.value = false
  }
}

function editCampaign() {
  router.push(`/campaigns/${campaign.value!.id}/edit`)
}

async function searchContacts(query: string) {
  if (!query) return
  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/contacts?search=${query}&page_size=10`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) return
    const data = await res.json()
    contactOptions.value = (data.items || []).map((c: any) => ({
      id: c.id,
      name: `${c.first_name} ${c.last_name}`,
    }))
  } catch {
    // ignore
  }
}

async function addMember() {
  if (!newMember.contact_id) {
    ElMessage.warning('请选择联系人')
    return
  }

  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/campaigns/${campaign.value!.id}/members`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(newMember),
    })
    if (!res.ok) throw new Error('Add failed')
    ElMessage.success('成员已添加')
    showAddMember.value = false
    newMember.contact_id = ''
    await loadCampaign()
  } catch (e: any) {
    ElMessage.error('添加失败: ' + (e.message || ''))
  }
}

async function updateMemberStatus(member: CampaignMember, status: string) {
  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/campaigns/${campaign.value!.id}/members/${member.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ status }),
    })
    if (!res.ok) throw new Error('Update failed')
  } catch (e: any) {
    ElMessage.error('更新失败: ' + (e.message || ''))
    await loadCampaign()
  }
}

async function removeMember(member: CampaignMember) {
  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/campaigns/${campaign.value!.id}/members/${member.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('Remove failed')
    ElMessage.success('成员已移除')
    await loadCampaign()
  } catch (e: any) {
    ElMessage.error('移除失败: ' + (e.message || ''))
  }
}

onMounted(loadCampaign)
</script>

<style scoped>
.campaign-detail-page {
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

.detail-header h2 {
  margin: 0 0 6px;
  font-size: 20px;
  font-weight: 700;
  color: #080707;
}

.detail-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #706e6b;
}

.meta-sep {
  color: #dddbda;
}

.overview-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.info-section h3,
.members-section h3 {
  font-size: 14px;
  font-weight: 600;
  color: #080707;
  margin: 0 0 12px;
}

.roi-card {
  background: #f8f8f8;
  border: 1px solid #dddbda;
  border-radius: 3px;
  padding: 16px;
}

.roi-metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #e8e8e8;
}

.roi-metric:last-child {
  border-bottom: none;
}

.roi-label {
  font-size: 13px;
  color: #706e6b;
}

.roi-value {
  font-size: 15px;
  font-weight: 600;
  color: #080707;
}

.roi-excellent { color: #67c23a; }
.roi-good { color: #409eff; }
.roi-normal { color: #e6a23c; }
.roi-bad { color: #f56c6c; }

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
</style>