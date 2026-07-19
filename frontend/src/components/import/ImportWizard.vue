<template>
  <el-dialog v-model="visible" title="导入数据" width="700px" :close-on-click-modal="false">
    <el-steps :active="step" align-center finish-status="success" style="margin-bottom: 24px">
      <el-step title="选择文件" />
      <el-step title="字段映射" />
      <el-step title="导入结果" />
    </el-steps>

    <!-- Step 1: File Upload -->
    <div v-if="step === 0" class="iw-step">
      <el-upload
        drag
        accept=".csv"
        :auto-upload="false"
        :show-file-list="false"
        :on-change="handleFileChange"
      >
        <el-icon :size="40" class="iw-upload-icon"><upload-filled /></el-icon>
        <div class="iw-upload-text">将 CSV 文件拖到此处，或点击选择文件</div>
        <template #tip>
          <div class="el-upload__tip">仅支持 CSV 格式，第一行为列标题</div>
        </template>
      </el-upload>
      <div v-if="selectedFile" class="iw-file-info">
        已选择: {{ selectedFile.name }}
      </div>
    </div>

    <!-- Step 2: Field Mapping -->
    <div v-if="step === 1 && preview" class="iw-step">
      <h4 class="iw-section-title">预览数据（前10行）</h4>
      <el-table :data="previewRows" border size="small" max-height="200">
        <el-table-column
          v-for="col in preview.columns"
          :key="col"
          :label="col"
          :prop="col"
          min-width="120"
        />
      </el-table>

      <h4 class="iw-section-title" style="margin-top: 16px">字段映射</h4>
      <div class="iw-mapping">
        <div v-for="col in preview.columns" :key="col" class="iw-mapping-row">
          <span class="iw-mapping-csv">{{ col }}</span>
          <el-icon class="iw-mapping-arrow"><arrow-right /></el-icon>
          <el-select
            v-model="mapping[col]"
            placeholder="选择字段"
            size="small"
            style="width: 200px"
            :class="{ 'iw-mapping-warning': !mapping[col] }"
          >
            <el-option
              v-for="field in preview.available_fields"
              :key="field.name"
              :label="`${field.label}${field.required ? ' *' : ''}`"
              :value="field.name"
            />
            <el-option label="(不导入)" value="" />
          </el-select>
        </div>
      </div>
    </div>

    <!-- Step 3: Result -->
    <div v-if="step === 2 && result" class="iw-step">
      <el-result
        :icon="result.error_rows > 0 ? 'warning' : 'success'"
        :title="result.error_rows > 0 ? '导入完成，有错误' : '导入成功'"
        :sub-title="`成功 ${result.success_rows} 行，失败 ${result.error_rows} 行`"
      >
        <template #extra>
          <div v-if="result.errors.length > 0" class="iw-errors">
            <h4>错误详情</h4>
            <div v-for="err in result.errors" :key="err.row" class="iw-error-item">
              第 {{ err.row }} 行: {{ err.error }}
            </div>
          </div>
        </template>
      </el-result>
    </div>

    <template #footer>
      <el-button v-if="step > 0 && step < 2" @click="step--">上一步</el-button>
      <el-button v-if="step < 2" type="primary" :loading="loading" @click="handleNext">
        {{ step === 0 ? '下一步' : '开始导入' }}
      </el-button>
      <el-button v-else type="primary" @click="close">完成</el-button>
      <el-button v-if="step === 0" @click="close">取消</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { UploadFilled, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { importExportApi } from '../../api/importExport'
import type { ImportPreview, ImportResult } from '../../types/importJob'

const props = defineProps<{
  objectType: string
}>()

const emit = defineEmits<{
  'done': []
}>()

const visible = ref(false)
const step = ref(0)
const loading = ref(false)
const selectedFile = ref<File | null>(null)
const preview = ref<ImportPreview | null>(null)
const mapping = ref<Record<string, string>>({})
const result = ref<ImportResult | null>(null)

const previewRows = computed(() => {
  if (!preview.value) return []
  return preview.value.preview_rows.map(row => {
    const obj: Record<string, string> = {}
    preview.value!.columns.forEach((col, idx) => {
      obj[col] = row[idx] || ''
    })
    return obj
  })
})

function open() {
  visible.value = true
  step.value = 0
  selectedFile.value = null
  preview.value = null
  result.value = null
}

function close() {
  visible.value = false
  emit('done')
}

function handleFileChange(file: any) {
  selectedFile.value = file.raw
}

async function handleNext() {
  if (step.value === 0) {
    if (!selectedFile.value) {
      ElMessage.warning('请选择文件')
      return
    }
    loading.value = true
    try {
      const { data } = await importExportApi.upload(selectedFile.value, props.objectType)
      preview.value = data
      // Initialize mapping with suggestions
      mapping.value = {}
      for (const [col, field] of Object.entries(data.mapping_suggestions)) {
        mapping.value[col] = field || ''
      }
      step.value = 1
    } catch (e: any) {
      ElMessage.error(e?.response?.data?.detail || '导入失败')
    } finally {
      loading.value = false
    }
  } else if (step.value === 1) {
    loading.value = true
    try {
      if (!preview.value) return
      const { data } = await importExportApi.confirm({
        preview_id: preview.value.preview_id,
        mapping: mapping.value,
      })
      result.value = data
      step.value = 2
    } catch (e: any) {
      ElMessage.error(e?.response?.data?.detail || '导入失败')
    } finally {
      loading.value = false
    }
  }
}

defineExpose({ open })
</script>

<style scoped>
.iw-step { min-height: 200px; }
.iw-upload-icon { margin-bottom: 8px; }
.iw-upload-text { font-size: 14px; color: #606266; margin-bottom: 8px; }
.iw-file-info { margin-top: 12px; padding: 8px; background: #f5f7fa; border-radius: 4px; font-size: 13px; }
.iw-section-title { font-size: 14px; font-weight: 600; color: #333; margin: 0 0 8px; }
.iw-mapping { display: flex; flex-direction: column; gap: 8px; }
.iw-mapping-row {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 8px; background: #fafafa; border-radius: 4px;
}
.iw-mapping-csv { font-size: 13px; font-weight: 500; min-width: 120px; color: #333; }
.iw-mapping-arrow { color: #c0c4cc; }
.iw-mapping-warning :deep(.el-select__wrapper) { background: #fff3e0; }
.iw-errors { max-height: 200px; overflow-y: auto; margin-top: 8px; }
.iw-error-item { font-size: 12px; color: #f56c6c; padding: 2px 0; }
</style>