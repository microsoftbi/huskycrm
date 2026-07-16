<template>
  <div class="dashboard-page">
    <div class="dash-header">
      <h2 class="page-title">仪表盘</h2>
      <el-button type="primary" icon="plus" @click="showCreateDialog = true">新建仪表盘</el-button>
    </div>

    <el-select v-model="selectedDashboard" placeholder="选择仪表盘" style="width:300px;margin-bottom:20px" @change="fetchDashboard">
      <el-option v-for="d in dashboards" :key="d.id" :label="d.name" :value="d.id" />
    </el-select>

    <template v-if="currentDashboard">
      <el-button size="small" type="danger" plain @click="handleDeleteDashboard" style="margin-left:10px">删除</el-button>

      <div class="dashboard-grid">
        <div
          v-for="comp in currentDashboard.components"
          :key="comp.id"
          class="dashboard-tile"
          :style="tileStyle(comp)"
        >
          <el-card shadow="hover" class="tile-card">
            <template #header>
              <div class="tile-header">
                <span>{{ comp.title }}</span>
                <el-button size="small" type="danger" text @click="removeComponent(comp.id)">
                  <el-icon><close /></el-icon>
                </el-button>
              </div>
            </template>
            <div class="tile-body" v-loading="compLoading[comp.id]">
              <el-table v-if="compData[comp.id]" :data="compRows[comp.id]" stripe size="small" max-height="300">
                <el-table-column v-for="col in compData[comp.id].columns" :key="col" :label="col" :prop="col" min-width="100" />
              </el-table>
              <el-empty v-else description="暂无数据" />
            </div>
          </el-card>
        </div>
      </div>

      <el-button size="small" type="primary" plain @click="showAddComponent = true" style="margin-top:16px">
        + 添加组件
      </el-button>
    </template>

    <el-empty v-if="dashboards.length === 0" description="暂无仪表盘，请先创建" />

    <!-- Create Dialog -->
    <el-dialog v-model="showCreateDialog" title="新建仪表盘" width="400px">
      <el-input v-model="newDashboardName" placeholder="仪表盘名称" />
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createDashboard">创建</el-button>
      </template>
    </el-dialog>

    <!-- Add Component Dialog -->
    <el-dialog v-model="showAddComponent" title="添加组件" width="500px">
      <el-form label-position="top">
        <el-form-item label="报表">
          <el-select v-model="newComponent.report_id" placeholder="选择报表" style="width:100%">
            <el-option v-for="r in reports" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="newComponent.title" placeholder="组件标题" />
        </el-form-item>
        <el-form-item label="图表类型">
          <el-select v-model="newComponent.chart_type" style="width:100%">
            <el-option label="表格" value="table" />
            <el-option label="指标" value="metric" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddComponent = false">取消</el-button>
        <el-button type="primary" @click="addComponent">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { dashboardsApi, reportsApi, type Dashboard, type ReportDef, type ReportResult } from '../../api/workflows'

const dashboards = ref<Dashboard[]>([])
const selectedDashboard = ref<number | null>(null)
const currentDashboard = ref<Dashboard | null>(null)
const reports = ref<ReportDef[]>([])
const compData = reactive<Record<number, ReportResult | null>>({})
const compLoading = reactive<Record<number, boolean>>({})
const showCreateDialog = ref(false)
const showAddComponent = ref(false)
const newDashboardName = ref('')

const newComponent = reactive({
  report_id: null as number | null,
  title: '',
  chart_type: 'table',
})

const compRows = computed(() => {
  const result: Record<number, any[]> = {}
  Object.entries(compData).forEach(([id, data]) => {
    if (data) {
      result[Number(id)] = data.rows.map((row: any[]) => {
        const obj: Record<string, any> = {}
        data.columns.forEach((col, i) => { obj[col] = row[i] })
        return obj
      })
    } else {
      result[Number(id)] = []
    }
  })
  return result
})

function tileStyle(comp: any) {
  return {
    gridColumn: `span ${Math.min(comp.width || 4, 6)}`,
    gridRow: `span ${Math.min(comp.height || 3, 4)}`,
  }
}

async function fetchDashboards() {
  try {
    const { data } = await dashboardsApi.list()
    dashboards.value = data
    if (data.length > 0 && !selectedDashboard.value) {
      selectedDashboard.value = data[0].id
      await fetchDashboard()
    }
  } catch { /* ignore */ }
}

async function fetchDashboard() {
  if (!selectedDashboard.value) return
  try {
    const { data } = await dashboardsApi.get(selectedDashboard.value)
    currentDashboard.value = data
    // Load each component's data
    for (const comp of data.components) {
      loadComponentData(comp.report_id, comp.id)
    }
  } catch { /* ignore */ }
}

async function loadComponentData(reportId: number, compId: number) {
  compLoading[compId] = true
  try {
    const { data } = await reportsApi.run(reportId, { page_size: 10 })
    compData[compId] = data
  } catch {
    compData[compId] = null
  } finally {
    compLoading[compId] = false
  }
}

async function createDashboard() {
  if (!newDashboardName.value) { ElMessage.warning('请输入名称'); return }
  try {
    const { data } = await dashboardsApi.create({ name: newDashboardName.value })
    dashboards.value.push(data)
    selectedDashboard.value = data.id
    currentDashboard.value = data
    showCreateDialog.value = false
    newDashboardName.value = ''
    ElMessage.success('创建成功')
  } catch { ElMessage.error('创建失败') }
}

async function addComponent() {
  if (!selectedDashboard.value || !newComponent.report_id) { ElMessage.warning('请选择报表'); return }
  try {
    const { data } = await dashboardsApi.addComponent(selectedDashboard.value, {
      report_id: newComponent.report_id,
      title: newComponent.title || '组件',
      chart_type: newComponent.chart_type,
    })
    await fetchDashboard()
    showAddComponent.value = false
    ElMessage.success('添加成功')
  } catch { ElMessage.error('添加失败') }
}

async function removeComponent(compId: number) {
  if (!selectedDashboard.value) return
  try {
    await dashboardsApi.deleteComponent(selectedDashboard.value, compId)
    await fetchDashboard()
    ElMessage.success('已删除')
  } catch { /* ignore */ }
}

async function handleDeleteDashboard() {
  if (!currentDashboard.value) return
  try {
    await ElMessageBox.confirm('确定删除此仪表盘？', '确认', { type: 'warning' })
    await dashboardsApi.delete(currentDashboard.value.id)
    ElMessage.success('已删除')
    currentDashboard.value = null
    selectedDashboard.value = null
    fetchDashboards()
  } catch { /* cancelled */ }
}

onMounted(async () => {
  await fetchDashboards()
  try {
    const { data } = await reportsApi.list()
    reports.value = data
  } catch { /* ignore */ }
})
</script>

<style scoped>
.dashboard-page { max-width: 1400px; }
.dash-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
}
.page-title { margin: 0; font-size: 22px; color: #333; }
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 16px;
  margin-top: 16px;
}
.dashboard-tile { min-width: 0; }
.tile-card { height: 100%; }
.tile-header { display: flex; justify-content: space-between; align-items: center; }
.tile-body { overflow-x: auto; }
</style>