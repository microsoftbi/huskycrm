<template>
  <div class="workflow-builder" v-loading="loading">
    <div class="builder-header">
      <el-button @click="$router.push('/admin/workflows')" icon="arrow-left" text>返回</el-button>
      <h2 class="page-title">{{ isNew ? '新建规则' : '编辑规则' }}</h2>
    </div>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header><span>基本信息</span></template>
          <el-form label-position="top">
            <el-form-item label="规则名称">
              <el-input v-model="form.name" placeholder="如: 大额机会通知" />
            </el-form-item>
            <el-form-item label="对象类型">
              <el-select v-model="form.object_type" style="width:100%">
                <el-option label="账户" value="account" />
                <el-option label="联系人" value="contact" />
                <el-option label="机会" value="opportunity" />
                <el-option label="发票" value="custom_invoice" />
              </el-select>
            </el-form-item>
            <el-form-item label="触发事件">
              <el-select v-model="form.trigger_event" style="width:100%">
                <el-option label="创建时" value="create" />
                <el-option label="更新时" value="update" />
                <el-option label="创建或更新" value="create_or_update" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="section-header">
              <span>条件 (AND)</span>
              <el-button size="small" icon="plus" @click="addCondition">添加</el-button>
            </div>
          </template>
          <div v-for="(cond, i) in form.condition_expression" :key="i" class="condition-row">
            <el-row :gutter="8">
              <el-col :span="6">
                <el-input v-model="cond.field" placeholder="字段名" size="small" />
              </el-col>
              <el-col :span="8">
                <el-select v-model="cond.operator" size="small" style="width:100%">
                  <el-option label="等于" value="eq" />
                  <el-option label="不等于" value="ne" />
                  <el-option label="大于" value="gt" />
                  <el-option label="大于等于" value="gte" />
                  <el-option label="小于" value="lt" />
                  <el-option label="小于等于" value="lte" />
                  <el-option label="包含" value="contains" />
                </el-select>
              </el-col>
              <el-col :span="8">
                <el-input v-model="cond.value" placeholder="值" size="small" />
              </el-col>
              <el-col :span="2">
                <el-button size="small" type="danger" text @click="removeCondition(i)">
                  <el-icon><close /></el-icon>
                </el-button>
              </el-col>
            </el-row>
          </div>
          <el-empty v-if="form.condition_expression.length === 0" description="无条件（始终触发）" />
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="section-header">
              <span>动作</span>
              <el-button size="small" icon="plus" @click="addAction">添加</el-button>
            </div>
          </template>
          <div v-for="(action, i) in form.actions" :key="i" class="action-card">
            <div class="action-header">
              <el-tag size="small">{{ actionLabels[action.action_type] || action.action_type }}</el-tag>
              <el-button size="small" type="danger" text @click="removeAction(i)">
                <el-icon><close /></el-icon>
              </el-button>
            </div>
            <el-input v-if="action.action_type === 'send_notification'" v-model="action.action_config.message" placeholder="通知消息" size="small" />
            <template v-if="action.action_type === 'update_field'">
              <el-input v-model="action.action_config.field" placeholder="字段名" size="small" style="margin-top:8px" />
              <el-input v-model="action.action_config.value" placeholder="新值" size="small" style="margin-top:4px" />
            </template>
          </div>
          <el-empty v-if="form.actions.length === 0" description="暂无动作" />
        </el-card>
      </el-col>
    </el-row>

    <div style="margin-top:20px;text-align:center">
      <el-button type="primary" :loading="saving" size="large" @click="handleSave">保存规则</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { workflowsApi, type WorkflowRule } from '../../api/workflows'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const isNew = computed(() => !route.params.id)

const actionLabels: Record<string, string> = {
  send_notification: '发送通知', update_field: '更新字段', create_record: '创建记录',
}

const form = reactive({
  name: '', object_type: 'opportunity', trigger_event: 'create_or_update',
  condition_expression: [] as any[],
  actions: [] as { action_type: string; action_config: Record<string, any>; display_order: number }[],
})

function addCondition() { form.condition_expression.push({ field: '', operator: 'gt', value: '' }) }
function removeCondition(i: number) { form.condition_expression.splice(i, 1) }
function addAction() { form.actions.push({ action_type: 'send_notification', action_config: { message: '' }, display_order: form.actions.length }) }
function removeAction(i: number) { form.actions.splice(i, 1) }

onMounted(async () => {
  if (!isNew.value) {
    loading.value = true
    try {
      const { data } = await workflowsApi.get(route.params.id as string)
      form.name = data.name
      form.object_type = data.object_type
      form.trigger_event = data.trigger_event
      form.condition_expression = data.condition_expression || []
      form.actions = data.actions.map(a => ({ ...a }))
    } catch {
      ElMessage.error('规则不存在')
      router.push('/admin/workflows')
    } finally { loading.value = false }
  }
})

async function handleSave() {
  if (!form.name) { ElMessage.warning('请输入规则名称'); return }
  saving.value = true
  try {
    if (isNew.value) {
      await workflowsApi.create({ ...form, condition_expression: form.condition_expression.length > 0 ? form.condition_expression : null })
      ElMessage.success('创建成功')
    } else {
      await workflowsApi.update(route.params.id as string, { name: form.name, condition_expression: form.condition_expression })
      ElMessage.success('更新成功')
    }
    router.push('/admin/workflows')
  } catch { ElMessage.error('保存失败') }
  finally { saving.value = false }
}
</script>

<style scoped>
.workflow-builder { max-width: 1200px; }
.builder-header {
  display: flex; align-items: center; gap: 12px; margin-bottom: 20px;
}
.page-title { margin: 0; font-size: 22px; color: #333; }
.section-header { display: flex; justify-content: space-between; align-items: center; }
.condition-row { margin-bottom: 8px; }
.action-card {
  border: 1px solid #eee; border-radius: 6px; padding: 10px; margin-bottom: 8px;
}
.action-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
</style>