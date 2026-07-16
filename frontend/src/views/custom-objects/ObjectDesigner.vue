<template>
  <div class="object-designer" v-loading="loading">
    <div class="designer-header">
      <el-button @click="$router.push('/admin/objects')" icon="arrow-left" text>返回</el-button>
      <h2 class="page-title">{{ isNew ? '新建对象' : `设计: ${object?.label}` }}</h2>
    </div>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header><span>对象属性</span></template>
          <el-form label-position="top">
            <el-form-item label="API 名称" prop="form.api_name" :rules="[{required: true}]">
              <el-input v-model="form.api_name" :disabled="!isNew" placeholder="如: custom_invoice" />
            </el-form-item>
            <el-form-item label="显示名称" prop="form.label">
              <el-input v-model="form.label" placeholder="如: 发票" />
            </el-form-item>
            <el-form-item label="复数名称">
              <el-input v-model="form.plural_label" placeholder="如: 发票列表" />
            </el-form-item>
            <el-form-item label="描述">
              <el-input v-model="form.description" type="textarea" :rows="3" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="saving" @click="handleSave">
                {{ isNew ? '创建对象' : '保存修改' }}
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="fields-header">
              <span>字段定义</span>
              <el-button size="small" type="primary" icon="plus" @click="showFieldDialog = true">
                添加字段
              </el-button>
            </div>
          </template>

          <el-table :data="fields" stripe style="width: 100%">
            <el-table-column type="index" label="#" width="50" />
            <el-table-column prop="api_name" label="API 名称" width="140" />
            <el-table-column prop="label" label="显示名称" width="140" />
            <el-table-column label="类型" width="100">
              <template #default="{ row }">{{ typeLabels[row.field_type] || row.field_type }}</template>
            </el-table-column>
            <el-table-column label="必填" width="60">
              <template #default="{ row }">
                <el-icon v-if="row.is_required" color="#67c23a"><check /></el-icon>
              </template>
            </el-table-column>
            <el-table-column label="唯一" width="60">
              <template #default="{ row }">
                <el-icon v-if="row.is_unique" color="#67c23a"><check /></el-icon>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row, $index }">
                <el-button size="small" type="danger" plain @click="removeField($index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="fields.length === 0" description="尚未添加字段" />
        </el-card>
      </el-col>
    </el-row>

    <!-- Add Field Dialog -->
    <el-dialog v-model="showFieldDialog" title="添加字段" width="500px">
      <el-form ref="fieldFormRef" :model="newField" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="API 名称" prop="api_name" :rules="[{required: true, message: '必填'}]">
              <el-input v-model="newField.api_name" placeholder="如: amount" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="显示名称" prop="label" :rules="[{required: true, message: '必填'}]">
              <el-input v-model="newField.label" placeholder="如: 金额" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="字段类型" prop="field_type">
          <el-select v-model="newField.field_type" style="width:100%">
            <el-option v-for="(label, type) in typeLabels" :key="type" :label="label" :value="type" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="必填">
              <el-switch v-model="newField.is_required" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="唯一">
              <el-switch v-model="newField.is_unique" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item v-if="newField.field_type === 'picklist'" label="选项值">
          <el-select v-model="newField.picklist_values" multiple allow-create filterable default-first-option style="width:100%" placeholder="输入选项后回车添加">
            <el-option v-for="item in newField.picklist_values" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showFieldDialog = false">取消</el-button>
        <el-button type="primary" @click="addField">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { customObjectsApi } from '../../api/customObjects'
import type { CustomObjectDef, CustomFieldCreate } from '../../types/crm'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const object = ref<CustomObjectDef | null>(null)
const fields = ref<CustomFieldCreate[]>([])
const showFieldDialog = ref(false)
const fieldFormRef = ref()

const isNew = computed(() => !route.params.id)

const form = reactive({
  api_name: '',
  label: '',
  plural_label: '',
  description: '',
})

const newField = reactive<CustomFieldCreate>({
  api_name: '',
  label: '',
  field_type: 'text',
  is_required: false,
  is_unique: false,
  picklist_values: [],
})

const typeLabels: Record<string, string> = {
  text: '文本',
  textarea: '多行文本',
  number: '数字',
  integer: '整数',
  boolean: '布尔',
  date: '日期',
  datetime: '日期时间',
  email: '邮箱',
  phone: '电话',
  url: '链接',
  picklist: '下拉选择',
  lookup: '关联对象',
}

onMounted(async () => {
  if (!isNew.value) {
    loading.value = true
    try {
      const { data } = await customObjectsApi.getObject(Number(route.params.id))
      object.value = data
      form.api_name = data.api_name
      form.label = data.label
      form.plural_label = data.plural_label || ''
      form.description = data.description || ''
      fields.value = data.fields.map(f => ({
        api_name: f.api_name,
        label: f.label,
        field_type: f.field_type,
        is_required: f.is_required,
        is_unique: f.is_unique,
        picklist_values: f.picklist_values || [],
      }))
    } catch {
      ElMessage.error('对象不存在')
      router.push('/admin/objects')
    } finally {
      loading.value = false
    }
  }
})

function addField() {
  if (!newField.api_name || !newField.label) {
    ElMessage.warning('请填写字段名称')
    return
  }
  fields.value.push({ ...newField })
  // Reset
  newField.api_name = ''
  newField.label = ''
  newField.field_type = 'text'
  newField.is_required = false
  newField.is_unique = false
  newField.picklist_values = []
  showFieldDialog.value = false
  ElMessage.success('字段已添加')
}

function removeField(index: number) {
  fields.value.splice(index, 1)
}

async function handleSave() {
  if (!form.api_name || !form.label) {
    ElMessage.warning('请填写对象名称和 API 名称')
    return
  }

  saving.value = true
  try {
    if (isNew.value) {
      await customObjectsApi.createObject({
        api_name: form.api_name,
        label: form.label,
        plural_label: form.plural_label || undefined,
        description: form.description || undefined,
        fields: fields.value,
      })
      ElMessage.success('对象创建成功')
    }
    router.push('/admin/objects')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.object-designer { max-width: 1200px; }
.designer-header {
  display: flex; align-items: center; gap: 12px; margin-bottom: 20px;
}
.page-title { margin: 0; font-size: 22px; color: #333; }
.fields-header {
  display: flex; justify-content: space-between; align-items: center;
}
</style>