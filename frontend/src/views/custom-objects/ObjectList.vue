<template>
  <div class="object-list">
    <div class="list-header">
      <h2 class="page-title">自定义对象</h2>
      <router-link to="/admin/objects/new">
        <el-button type="primary" icon="plus">新建对象</el-button>
      </router-link>
    </div>

    <el-card shadow="hover">
      <el-table :data="objects" stripe v-loading="loading" style="width: 100%">
        <el-table-column type="index" label="#" width="60" />
        <el-table-column label="对象名称" min-width="180">
          <template #default="{ row }">
            <router-link :to="`/admin/objects/${row.id}`">
              <el-link type="primary">{{ row.label }}</el-link>
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="api_name" label="API 名称" width="180" />
        <el-table-column label="字段数" width="100">
          <template #default="{ row }">{{ row.fields?.length || 0 }}</template>
        </el-table-column>
        <el-table-column prop="table_name" label="数据表" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '活跃' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/admin/objects/${row.id}`)">设计</el-button>
            <el-button size="small" @click="$router.push(`/admin/objects/${row.id}/records`)">数据</el-button>
            <el-button size="small" type="danger" plain @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && objects.length === 0" description="暂无自定义对象" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { customObjectsApi } from '../../api/customObjects'
import type { CustomObjectDef } from '../../types/crm'

const objects = ref<CustomObjectDef[]>([])
const loading = ref(false)

async function fetchObjects() {
  loading.value = true
  try {
    const { data } = await customObjectsApi.listObjects()
    objects.value = data
  } catch {
    ElMessage.error('获取对象列表失败')
  } finally {
    loading.value = false
  }
}

async function handleDelete(row: CustomObjectDef) {
  try {
    await ElMessageBox.confirm(
      `确定删除对象 "${row.label}" 吗？所有数据将被永久删除。`,
      '确认删除',
      { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }
    )
    await customObjectsApi.deleteObject(row.id)
    ElMessage.success('删除成功')
    fetchObjects()
  } catch { /* cancelled */ }
}

onMounted(fetchObjects)
</script>

<style scoped>
.object-list { max-width: 1200px; }
.list-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
}
.page-title { margin: 0; font-size: 22px; color: #333; }
</style>