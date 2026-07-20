<template>
  <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
    <el-form-item label="区域名称" prop="name">
      <el-input v-model="form.name" placeholder="如：亚太区" />
    </el-form-item>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-form-item label="区域编码">
          <el-input v-model="form.code" placeholder="如：APAC" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="区域类型">
          <el-select v-model="form.territory_type" style="width:100%">
            <el-option label="大区" value="region" />
            <el-option label="区域" value="district" />
            <el-option label="分部" value="branch" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-form-item label="上级区域">
      <el-tree-select
        v-model="form.parent_id"
        :data="treeData"
        :props="{ label: 'name', value: 'id' }"
        placeholder="选择上级区域（留空为根区域）"
        clearable
        check-strictly
        style="width:100%"
      />
    </el-form-item>

    <el-form-item label="区域负责人">
      <el-select v-model="form.owner_id" placeholder="选择负责人" clearable filterable style="width:100%">
        <el-option v-for="u in users" :key="u.id" :label="u.display_name || u.username" :value="u.id" />
      </el-select>
    </el-form-item>

    <el-form-item label="描述">
      <el-input v-model="form.description" type="textarea" :rows="3" placeholder="备注信息" />
    </el-form-item>

    <el-form-item>
      <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      <el-button @click="$emit('cancel')">取消</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { territoriesApi } from '../../api/territories'
import { authApi } from '../../api/auth'
import type { TerritoryTreeNode } from '../../types/territory'

const props = defineProps<{ territoryId?: string | null }>()
const emit = defineEmits<{ saved: []; cancel: [] }>()

const formRef = ref()
const saving = ref(false)
const treeData = ref<TerritoryTreeNode[]>([])
const users = ref<{ id: number; username: string; display_name?: string }[]>([])

const form = reactive({
  name: '',
  code: '',
  territory_type: 'region',
  parent_id: null as string | null,
  owner_id: null as string | null,
  description: '',
})

const rules = {
  name: [{ required: true, message: '请输入区域名称', trigger: 'blur' }],
}

async function handleSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const data: any = { ...form }
    if (!data.code) delete data.code
    if (!data.parent_id) data.parent_id = null
    if (!data.owner_id) data.owner_id = null
    if (!data.description) delete data.description

    if (props.territoryId) {
      await territoriesApi.update(props.territoryId, data)
      ElMessage.success('更新成功')
    } else {
      await territoriesApi.create(data)
      ElMessage.success('创建成功')
    }
    emit('saved')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await territoriesApi.getTree()
    // Filter out self and descendants when editing
    treeData.value = data
  } catch { /* ignore */ }

  try {
    const { data } = await authApi.listUsers()
    users.value = data.items
  } catch { /* ignore */ }

  if (props.territoryId) {
    try {
      const { data } = await territoriesApi.get(props.territoryId)
      form.name = data.name
      form.code = data.code || ''
      form.territory_type = data.territory_type
      form.parent_id = data.parent_id
      form.owner_id = data.owner_id
      form.description = data.description || ''
    } catch {
      ElMessage.error('区域不存在')
      emit('cancel')
    }
  }
})
</script>
