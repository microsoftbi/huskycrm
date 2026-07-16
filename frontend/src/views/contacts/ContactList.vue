<template>
  <div class="contact-list">
    <div class="sf-page-header">
      <h2 class="sf-page-title">联系人</h2>
      <div class="sf-page-actions">
        <router-link to="/contacts/new">
          <el-button type="primary" size="small" icon="plus">新建联系人</el-button>
        </router-link>
      </div>
    </div>

    <div class="sf-card">
      <div class="sf-filter-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索姓名或邮箱..."
          clearable
          size="small"
          @clear="fetchContacts"
          @keyup.enter="fetchContacts"
        >
          <template #prefix><el-icon><search /></el-icon></template>
        </el-input>
      </div>

      <el-table :data="contacts" stripe v-loading="loading" class="sf-table-compact" size="small" style="width:100%">
        <el-table-column type="index" label="#" width="60" />
        <el-table-column label="姓名" min-width="180">
          <template #default="{ row }">
            <router-link :to="`/contacts/${row.id}`">
              <el-link type="primary">{{ row.first_name }} {{ row.last_name }}</el-link>
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="200" />
        <el-table-column prop="phone" label="电话" width="140" />
        <el-table-column prop="title" label="职位" width="160" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/contacts/${row.id}`)">查看</el-button>
            <el-button size="small" type="danger" plain @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="padding:10px 14px;display:flex;justify-content:flex-end;border-top:1px solid #dddbda;">
        <el-pagination
          v-model:current-page="page" v-model:page-size="pageSize"
          :total="total" :page-sizes="[10,20,50]"
          layout="total, sizes, prev, pager, next"
          size="small" @change="fetchContacts"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { contactsApi } from '../../api/contacts'
import type { Contact } from '../../types/crm'

const contacts = ref<Contact[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const searchQuery = ref('')

async function fetchContacts() {
  loading.value = true
  try {
    const { data } = await contactsApi.list({ page: page.value, page_size: pageSize.value, search: searchQuery.value })
    contacts.value = data.items
    total.value = data.total
  } finally { loading.value = false }
}

async function handleDelete(row: Contact) {
  try {
    await ElMessageBox.confirm(`确定删除 "${row.first_name} ${row.last_name}" 吗？`, '确认删除', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
    await contactsApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchContacts()
  } catch { /* cancelled */ }
}

onMounted(fetchContacts)
</script>

<style scoped>
.contact-list { max-width: 1200px; }
</style>
