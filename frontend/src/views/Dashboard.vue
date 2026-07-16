<template>
  <div class="dashboard">
    <div class="sf-page-header">
      <h2 class="sf-page-title">仪表盘</h2>
    </div>

    <el-row :gutter="16" class="stats-row">
      <el-col :span="8">
        <div class="sf-card">
          <div class="sf-card-body" style="display:flex;align-items:center;gap:16px;">
            <div style="width:48px;height:48px;border-radius:4px;background:#e8f0fe;display:flex;align-items:center;justify-content:center;color:#1589ee;font-size:24px;">
              <el-icon :size="24"><office-building /></el-icon>
            </div>
            <div>
              <div style="font-size:24px;font-weight:700;color:#080707;">{{ stats.totalAccounts }}</div>
              <div style="font-size:12px;color:#706e6b;">账户总数</div>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="sf-card">
          <div class="sf-card-body" style="display:flex;align-items:center;gap:16px;">
            <div style="width:48px;height:48px;border-radius:4px;background:#f0f9eb;display:flex;align-items:center;justify-content:center;color:#2e844a;font-size:24px;">
              <el-icon :size="24"><user /></el-icon>
            </div>
            <div>
              <div style="font-size:24px;font-weight:700;color:#080707;">{{ stats.totalContacts }}</div>
              <div style="font-size:12px;color:#706e6b;">联系人总数</div>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="sf-card">
          <div class="sf-card-body" style="display:flex;align-items:center;gap:16px;">
            <div style="width:48px;height:48px;border-radius:4px;background:#fef0f0;display:flex;align-items:center;justify-content:center;color:#c23934;font-size:24px;">
              <el-icon :size="24"><trend-chart /></el-icon>
            </div>
            <div>
              <div style="font-size:24px;font-weight:700;color:#080707;">{{ stats.totalOpps }}</div>
              <div style="font-size:12px;color:#706e6b;">机会总数</div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="12">
        <div class="sf-card">
          <div class="sf-card-header">
            <span>最新账户</span>
            <router-link to="/accounts"><el-link type="primary" style="font-size:12px;">查看全部</el-link></router-link>
          </div>
          <div class="sf-card-body" style="padding:0;">
            <el-table :data="recentAccounts" class="sf-table-compact" size="small" stripe style="width:100%" v-loading="loadingAccounts">
              <el-table-column prop="name" label="名称" />
              <el-table-column prop="industry" label="行业" width="120" />
              <el-table-column prop="phone" label="电话" width="140" />
            </el-table>
          </div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="sf-card">
          <div class="sf-card-header">
            <span>最新联系人</span>
            <router-link to="/contacts"><el-link type="primary" style="font-size:12px;">查看全部</el-link></router-link>
          </div>
          <div class="sf-card-body" style="padding:0;">
            <el-table :data="recentContacts" class="sf-table-compact" size="small" stripe style="width:100%" v-loading="loadingContacts">
              <el-table-column label="姓名" width="160">
                <template #default="{ row }">{{ row.first_name }} {{ row.last_name }}</template>
              </el-table-column>
              <el-table-column prop="email" label="邮箱" />
              <el-table-column prop="phone" label="电话" width="140" />
            </el-table>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { accountsApi } from '../api/accounts'
import { contactsApi } from '../api/contacts'
import { opportunitiesApi } from '../api/opportunities'

const stats = reactive({ totalAccounts: 0, totalContacts: 0, totalOpps: 0 })
const recentAccounts = ref([])
const recentContacts = ref([])
const loadingAccounts = ref(false)
const loadingContacts = ref(false)

onMounted(async () => {
  try {
    loadingAccounts.value = true
    const accRes = await accountsApi.list({ page: 1, page_size: 5 })
    recentAccounts.value = accRes.data.items
    stats.totalAccounts = accRes.data.total
  } finally { loadingAccounts.value = false }

  try {
    loadingContacts.value = true
    const conRes = await contactsApi.list({ page: 1, page_size: 5 })
    recentContacts.value = conRes.data.items
    stats.totalContacts = conRes.data.total
  } finally { loadingContacts.value = false }

  try {
    const oppRes = await opportunitiesApi.list({ page: 1, page_size: 1 })
    stats.totalOpps = oppRes.data.total
  } catch { /* ignore */ }
})
</script>

<style scoped>
.dashboard { max-width: 1200px; }
.stats-row { margin-bottom: 16px; }
</style>
