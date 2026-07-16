<template>
  <div class="report-builder" v-loading="loading">
    <div class="builder-header">
      <el-button @click="$router.push('/admin/reports')" icon="arrow-left" text>返回</el-button>
      <h2 class="page-title">{{ isNew ? '新建报表' : '编辑报表' }}</h2>
    </div>

    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header><span>报表设置</span></template>
          <el-form label-position="top">
            <el-form-item label="报表名称">
              <el-input v-model="form.name" />
            </el-form-item>
            <el-form-item label="对象">
              <el-select v-model="form.object_type" style="width:100%">
                <el-option label="账户" value="account" />
                <el-option label="联系人" value="contact" />
                <el-option label="机会" value="opportunity" />
              </el-select>
            </el-form-item>
            <el-form-item label="类型">
              <el-select v-model="form.report_type" style="width:100%">
                <el-option label="列表" value="tabular" />
                <el-option label="汇总" value="summary" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="18">
        <el-card shadow="hover">
          <template #header>
            <div class="section-header">
              <span>显示列</span>
              <el-button size="small" icon="plus" @click="addColumn">添加列</el-button>
            </div>
          </template>
          <div v-for="(col, i) in form.columns" :key="i" class="column-item">
            <el-input v-model="form.columns[i]" size="small" placeholder="字段名" style="width:200px" />
            <el-button size="small" type="danger" text @click="form.columns.splice(i, 1)">
              <el-icon><close /></el-icon>
            </el-button>
          </div>
          <el-empty v-if="!form.columns || form.columns.length === 0" description="点击【添加列】选择字段" />
        </el-card>

        <el-card shadow="hover" style="margin-top:16px">
          <template #header><span>筛选条件</span></template>
          <div v-for="(f, i) in form.filters" :key="i" class="filter-row">
            <el-row :gutter="8">
              <el-col :span="6"><el-input v-model="f.field" placeholder="字段" size="small" /></el-col>
              <el-col :span="6">
                <el-select v-model="f.operator" size="small" style="width:100%">
                  <el-option label="等于" value="eq" />
                  <el-option label="大于" value="gt" />
                  <el-option label="小于" value="lt" />
                  <el-option label="包含" value="contains" />
                </el-select>
              </el-col>
              <el-col :span="8"><el-input v-model="f.value" placeholder="值" size="small" /></el-col>
              <el-col :span="4">
                <el-button size="small" type="danger" text @click="form.filters.splice(i, 1)">删除</el-button>
              </el-col>
            </el-row>
          </div>
          <el-button size="small" @click="addFilter">+ 添加筛选</el-button>
        </el-card>
      </el-col>
    </el-row>

    <div style="margin-top:20px;text-align:center">
      <el-button type="primary" :loading="saving" size="large" @click="handleSave">保存报表</el-button>
      <el-button size="large" @click="handleRun">运行</el-button>
    </div>

    <!-- Results -->
    <el-dialog v-model="showResults" title="预览结果" width="80%" top="5vh">
      <el-table :data="previewRows" stripe border max-height="500" v-if="preview">
        <el-table-column v-for="col in preview.columns" :key="col" :label="col" :prop="col" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { reportsApi } from '../../api/workflows'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const showResults = ref(false)
const preview = ref<any>(null)
const isNew = computed(() => !route.params.id)

const form = reactive({
  name: '', object_type: 'account', report_type: 'tabular',
  columns: ['id', 'name', 'industry', 'phone', 'email'] as string[],
  filters: [] as any[],
  grouping: [] as string[],
  aggregations: [] as any[],
})

const previewRows = computed(() => {
  if (!preview.value) return []
  return preview.value.rows.map((row: any[]) => {
    const obj: Record<string, any> = {}
    preview.value.columns.forEach((col: string, i: number) => { obj[col] = row[i] })
    return obj
  })
})

function addColumn() { form.columns.push('') }
function addFilter() { form.filters.push({ field: '', operator: 'eq', value: '' }) }

onMounted(async () => {
  if (!isNew.value) {
    loading.value = true
    try {
      const { data } = await reportsApi.get(Number(route.params.id))
      form.name = data.name; form.object_type = data.object_type
      form.report_type = data.report_type; form.columns = data.columns || []
      form.filters = data.filters || []
    } catch {
      ElMessage.error('报表不存在'); router.push('/admin/reports')
    } finally { loading.value = false }
  }
})

async function handleSave() {
  if (!form.name) { ElMessage.warning('请输入报表名称'); return }
  saving.value = true
  try {
    const payload = { ...form, filters: form.filters.length ? form.filters : null, columns: form.columns.filter(Boolean) }
    if (isNew.value) {
      await reportsApi.create(payload)
      ElMessage.success('创建成功')
    } else {
      await reportsApi.update(Number(route.params.id), payload)
      ElMessage.success('更新成功')
    }
    router.push('/admin/reports')
  } catch { ElMessage.error('保存失败') }
  finally { saving.value = false }
}

async function handleRun() {
  const payload = { ...form, filters: form.filters.length ? form.filters : null, columns: form.columns.filter(Boolean) }
  try {
    let id = Number(route.params.id)
    if (!id) {
      const { data } = await reportsApi.create(payload)
      id = data.id
    }
    const { data } = await reportsApi.run(id)
    preview.value = data
    showResults.value = true
  } catch { ElMessage.error('运行失败') }
}
</script>

<style scoped>
.report-builder { max-width: 1200px; }
.builder-header {
  display: flex; align-items: center; gap: 12px; margin-bottom: 20px;
}
.page-title { margin: 0; font-size: 22px; color: #333; }
.section-header { display: flex; justify-content: space-between; align-items: center; }
.column-item { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.filter-row { margin-bottom: 8px; }
</style>