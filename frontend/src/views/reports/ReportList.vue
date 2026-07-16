<template>
  <div class="report-list">
    <div class="list-header">
      <h2 class="page-title">报表</h2>
      <router-link to="/admin/reports/new">
        <el-button type="primary" icon="plus">新建报表</el-button>
      </router-link>
    </div>

    <el-card shadow="hover">
      <el-table :data="reports" stripe v-loading="loading" style="width: 100%">
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="name" label="名称" min-width="200">
          <template #default="{ row }">
            <router-link :to="`/admin/reports/${row.id}`">
              <el-link type="primary">{{ row.name }}</el-link>
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="object_type" label="对象" width="120" />
        <el-table-column prop="report_type" label="类型" width="100" />
        <el-table-column label="列数" width="80">
          <template #default="{ row }">{{ row.columns?.length || 0 }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="runReport(row.id)">运行</el-button>
            <el-button size="small" @click="$router.push(`/admin/reports/${row.id}/edit`)">编辑</el-button>
            <el-button size="small" type="danger" plain @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && reports.length === 0" description="暂无报表" />
    </el-card>

    <!-- Report Results Dialog -->
    <el-dialog v-model="showResults" title="报表结果" width="80%" top="5vh">
      <el-table :data="resultRows" stripe border max-height="500" v-if="results">
        <el-table-column v-for="col in results.columns" :key="col" :label="col" :prop="col" />
      </el-table>
      <div v-if="results" style="margin-top:10px;color:#999;text-align:right">
        共 {{ results.total }} 条记录
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { reportsApi, type ReportDef, type ReportResult } from '../../api/workflows'

const reports = ref<ReportDef[]>([])
const loading = ref(false)
const showResults = ref(false)
const results = ref<ReportResult | null>(null)

const resultRows = computed(() => {
  if (!results.value) return []
  return results.value.rows.map((row: any[]) => {
    const obj: Record<string, any> = {}
    results.value!.columns.forEach((col, i) => { obj[col] = row[i] })
    return obj
  })
})

async function fetchReports() {
  loading.value = true
  try {
    const { data } = await reportsApi.list()
    reports.value = data
  } finally { loading.value = false }
}

async function runReport(id: number) {
  try {
    const { data } = await reportsApi.run(id)
    results.value = data
    showResults.value = true
  } catch { ElMessage.error('运行报表失败') }
}

async function handleDelete(row: ReportDef) {
  try {
    await ElMessageBox.confirm(`确定删除报表 "${row.name}" 吗？`, '确认删除', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
    await reportsApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchReports()
  } catch { /* cancelled */ }
}

onMounted(fetchReports)
</script>

<style scoped>
.report-list { max-width: 1200px; }
.list-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
}
.page-title { margin: 0; font-size: 22px; color: #333; }
</style>