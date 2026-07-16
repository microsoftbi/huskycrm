<template>
  <div class="record-detail" v-loading="loading">
    <div class="sf-page-header">
      <el-button @click="$router.push(`/admin/objects/${route.params.id}/records`)" icon="arrow-left" text>返回</el-button>
      <h2 class="sf-page-title">{{ object?.label || '记录详情' }}</h2>
    </div>

    <template v-if="record">
      <div class="sf-record-header">
        <div class="sf-record-icon">
          <el-icon :size="20"><grid /></el-icon>
        </div>
        <div class="sf-record-name">记录 #{{ record.id }}</div>
        <div class="sf-record-actions">
          <el-button type="primary" size="small" icon="edit" @click="showEdit = true">编辑</el-button>
          <el-button size="small" type="danger" plain icon="delete" @click="handleDelete">删除</el-button>
        </div>
      </div>

      <div class="sf-field-section">
        <div class="sf-field-section-title">字段信息</div>
        <div class="sf-field-row">
          <div v-for="(value, key) in record.fields" :key="key" class="sf-field">
            <div class="sf-field-label">{{ getFieldLabel(key) }}</div>
            <div class="sf-field-value">{{ formatValue(key, value) }}</div>
          </div>
        </div>
      </div>

      <div class="sf-field-section">
        <div class="sf-field-section-title">系统信息</div>
        <div class="sf-field-row">
          <div class="sf-field">
            <div class="sf-field-label">记录 ID</div>
            <div class="sf-field-value">{{ record.id }}</div>
          </div>
          <div class="sf-field">
            <div class="sf-field-label">UUID</div>
            <div class="sf-field-value">{{ record.record_id }}</div>
          </div>
          <div class="sf-field">
            <div class="sf-field-label">创建时间</div>
            <div class="sf-field-value">{{ record.created_at }}</div>
          </div>
          <div class="sf-field">
            <div class="sf-field-label">更新时间</div>
            <div class="sf-field-value">{{ record.updated_at }}</div>
          </div>
        </div>
      </div>
    </template>

    <!-- Edit dialog -->
    <el-dialog v-model="showEdit" title="编辑记录" width="600px" destroy-on-close>
      <el-form ref="editFormRef" :model="editForm" label-position="top" size="small">
        <el-form-item
          v-for="field in object?.fields || []"
          :key="field.api_name"
          :label="field.label"
          :required="field.is_required"
        >
          <el-input
            v-if="field.field_type === 'text' || field.field_type === 'email' || field.field_type === 'phone'"
            v-model="editForm[field.api_name]"
            :placeholder="`请输入${field.label}`"
          />
          <el-input-number
            v-else-if="field.field_type === 'number'"
            v-model="editForm[field.api_name]"
            :min="0"
            style="width: 100%"
          />
          <el-select
            v-else-if="field.field_type === 'picklist'"
            v-model="editForm[field.api_name]"
            :placeholder="`请选择${field.label}`"
            style="width: 100%"
          >
            <el-option
              v-for="opt in (field.picklist_values || [])"
              :key="opt"
              :label="opt"
              :value="opt"
            />
          </el-select>
          <el-switch v-else-if="field.field_type === 'boolean'" v-model="editForm[field.api_name]" />
          <el-input
            v-else
            v-model="editForm[field.api_name]"
            :placeholder="`请输入${field.label}`"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEdit = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSaveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { customObjectsApi } from '../../api/customObjects'
import type { CustomObjectDef, CustomRecord } from '../../types/crm'

const route = useRoute()
const router = useRouter()
const object = ref<CustomObjectDef | null>(null)
const record = ref<CustomRecord | null>(null)
const loading = ref(false)
const saving = ref(false)
const showEdit = ref(false)
const editForm = reactive<Record<string, any>>({})
const editFormRef = ref()

const objId = Number(route.params.id)
const recordId = Number(route.params.record_id)

function getFieldLabel(apiName: string): string {
  return object.value?.fields?.find(f => f.api_name === apiName)?.label || apiName
}

function formatValue(key: string, value: any): string {
  if (value === null || value === undefined) return '-'
  return String(value)
}

async function fetchData() {
  loading.value = true
  try {
    const [objResp, recResp] = await Promise.all([
      customObjectsApi.getObject(objId),
      customObjectsApi.getRecord(objId, recordId),
    ])
    object.value = objResp.data
    record.value = recResp.data
  } catch {
    ElMessage.error('记录不存在')
    router.push(`/admin/objects/${objId}/records`)
  } finally {
    loading.value = false
  }
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm('确定删除此记录吗？', '确认删除', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
    await customObjectsApi.deleteRecord(objId, recordId)
    ElMessage.success('删除成功')
    router.push(`/admin/objects/${objId}/records`)
  } catch { /* cancelled */ }
}

async function handleSaveEdit() {
  saving.value = true
  try {
    await customObjectsApi.updateRecord(objId, recordId, editForm)
    ElMessage.success('更新成功')
    showEdit.value = false
    fetchData()
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await fetchData()
  if (record.value?.fields) {
    Object.assign(editForm, record.value.fields)
  }
})
</script>

<style scoped>
.record-detail { max-width: 900px; }
</style>
