<template>
  <div class="object-records" v-loading="loading">
    <div class="records-header">
      <el-button @click="$router.push('/admin/objects')" icon="arrow-left" text>返回</el-button>
      <h2 class="page-title">{{ object?.label || '数据' }}</h2>
      <div style="flex:1" />
      <el-button type="primary" icon="plus" @click="showCreateDialog = true">新建记录</el-button>
    </div>

    <el-card shadow="hover">
      <el-table :data="records" stripe style="width: 100%">
        <el-table-column type="index" label="#" width="60" />
        <el-table-column
          v-for="field in displayFields"
          :key="field.api_name"
          :label="field.label"
          :min-width="field.field_type === 'textarea' ? 200 : 140"
        >
          <template #default="{ row }">
            <template v-if="field.field_type === 'boolean'">
              <el-icon v-if="row.fields[field.api_name]" color="#67c23a"><check /></el-icon>
              <span v-else>-</span>
            </template>
            <template v-else-if="field.field_type === 'picklist'">
              <el-tag size="small">{{ row.fields[field.api_name] || '-' }}</el-tag>
            </template>
            <template v-else>
              {{ row.fields[field.api_name] ?? '-' }}
            </template>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="editRecord(row)">编辑</el-button>
            <el-button size="small" type="danger" plain @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="records.length === 0 && !loading" style="text-align:center;padding:40px;color:#999">
        暂无数据记录
      </div>

      <div class="pagination-wrapper" v-if="total > pageSize">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          @change="fetchRecords"
        />
      </div>
    </el-card>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingRecord ? '编辑记录' : '新建记录'"
      width="600px"
    >
      <el-form ref="recordFormRef" label-position="top">
        <FieldRenderer
          v-for="field in object?.fields || []"
          :key="field.api_name"
          :field="field"
          v-model="recordFields"
        />
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSaveRecord">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { customObjectsApi } from '../../api/customObjects'
import type { CustomObjectDef, CustomRecord } from '../../types/crm'
import FieldRenderer from '../../components/dynamic-form/FieldRenderer.vue'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const object = ref<CustomObjectDef | null>(null)
const records = ref<CustomRecord[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const showCreateDialog = ref(false)
const editingRecord = ref<CustomRecord | null>(null)
const recordFormRef = ref()
const recordFields = reactive<Record<string, any>>({})

const displayFields = computed(() => {
  return (object.value?.fields || []).slice(0, 6)
})

const objId = computed(() => Number(route.params.id))

async function fetchObject() {
  try {
    const { data } = await customObjectsApi.getObject(objId.value)
    object.value = data
  } catch {
    ElMessage.error('对象不存在')
    router.push('/admin/objects')
  }
}

async function fetchRecords() {
  loading.value = true
  try {
    const { data } = await customObjectsApi.listRecords(objId.value, {
      page: page.value,
      page_size: pageSize.value,
    })
    records.value = data.items
    total.value = data.total
  } catch {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

function editRecord(row: CustomRecord) {
  editingRecord.value = row
  // Reset fields
  Object.keys(recordFields).forEach(k => delete recordFields[k])
  Object.assign(recordFields, row.fields)
  showCreateDialog.value = true
}

async function handleSaveRecord() {
  saving.value = true
  try {
    if (editingRecord.value) {
      await customObjectsApi.updateRecord(objId.value, editingRecord.value.id, { ...recordFields })
      ElMessage.success('更新成功')
    } else {
      await customObjectsApi.createRecord(objId.value, { ...recordFields })
      ElMessage.success('创建成功')
    }
    showCreateDialog.value = false
    editingRecord.value = null
    Object.keys(recordFields).forEach(k => delete recordFields[k])
    fetchRecords()
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(row: CustomRecord) {
  try {
    await ElMessageBox.confirm('确定删除此记录吗？', '确认删除', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
    await customObjectsApi.deleteRecord(objId.value, row.id)
    ElMessage.success('删除成功')
    fetchRecords()
  } catch { /* cancelled */ }
}

onMounted(async () => {
  await fetchObject()
  await fetchRecords()
})
</script>

<style scoped>
.object-records { max-width: 1200px; }
.records-header {
  display: flex; align-items: center; gap: 12px; margin-bottom: 20px;
}
.page-title { margin: 0; font-size: 22px; color: #333; }
.pagination-wrapper { margin-top: 20px; display: flex; justify-content: flex-end; }
</style>