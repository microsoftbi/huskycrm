<template>
  <div class="account-list">
    <div class="sf-page-header">
      <h2 class="sf-page-title">账户</h2>
      <div class="sf-page-actions">
        <router-link to="/accounts/new">
          <el-button type="primary" size="small" icon="plus">新建账户</el-button>
        </router-link>
      </div>
    </div>

    <div class="sf-card">
      <div class="sf-filter-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索账户名称..."
          clearable
          size="small"
          @clear="fetchAccounts"
          @keyup.enter="fetchAccounts"
        >
          <template #prefix><el-icon><search /></el-icon></template>
        </el-input>
      </div>

      <el-table
        :data="accounts"
        stripe
        v-loading="loading"
        style="width: 100%"
        class="sf-table-compact"
        size="small"
      >
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="name" label="名称" min-width="180">
          <template #default="{ row }">
            <router-link :to="`/accounts/${row.id}`">
              <el-link type="primary">{{ row.name }}</el-link>
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="industry" label="行业" width="140" />
        <el-table-column prop="phone" label="电话" width="140" />
        <el-table-column prop="email" label="邮箱" min-width="200" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/accounts/${row.id}`)">查看</el-button>
            <el-button size="small" type="danger" plain @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="padding: 10px 14px; display: flex; justify-content: flex-end; border-top: 1px solid #dddbda;">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          size="small"
          @change="fetchAccounts"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { accountsApi } from '../../api/accounts'
import type { Account } from '../../types/crm'

const accounts = ref<Account[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const searchQuery = ref('')

async function fetchAccounts() {
  loading.value = true
  try {
    const { data } = await accountsApi.list({
      page: page.value,
      page_size: pageSize.value,
      search: searchQuery.value,
    })
    accounts.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

async function handleDelete(row: Account) {
  try {
    await ElMessageBox.confirm(`确定删除账户 "${row.name}" 吗？`, '确认删除', {
      confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning',
    })
    await accountsApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchAccounts()
  } catch { /* cancelled */ }
}

onMounted(fetchAccounts)
</script>

<style scoped>
.account-list {
  max-width: 1200px;
}
</style>
