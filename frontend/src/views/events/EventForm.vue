<template>
  <div class="event-form" v-loading="loading">
    <div class="sf-page-header">
      <el-button @click="goBack" icon="arrow-left" text>返回</el-button>
      <h2 class="sf-page-title">{{ isEdit ? '编辑拜访' : '新建拜访' }}</h2>
    </div>

    <div class="sf-card">
      <div class="sf-card-body">
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" size="small">
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="拜访主题" prop="subject">
                <el-input v-model="form.subject" placeholder="请输入拜访主题" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="类型" prop="type">
                <el-select v-model="form.type" placeholder="选择类型" style="width:100%">
                  <el-option label="上门拜访" value="Visit" />
                  <el-option label="电话拜访" value="Phone Call" />
                  <el-option label="视频会议" value="Video Conference" />
                  <el-option label="客户来访" value="Client Visit" />
                  <el-option label="其他" value="Other" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="状态">
                <el-select v-model="form.status" disabled style="width:100%">
                  <el-option label="计划中" value="planned" />
                  <el-option label="进行中" value="in_progress" />
                  <el-option label="已完成" value="completed" />
                  <el-option label="已取消" value="cancelled" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="24">
            <el-col :span="8">
              <el-form-item label="计划开始时间" prop="start_datetime">
                <el-date-picker v-model="form.start_datetime" type="datetime" placeholder="选择开始时间" style="width:100%"
                  value-format="YYYY-MM-DDTHH:mm:ss" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="计划结束时间">
                <el-date-picker v-model="form.end_datetime" type="datetime" placeholder="选择结束时间" style="width:100%"
                  value-format="YYYY-MM-DDTHH:mm:ss" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="忙/闲状态">
                <el-select v-model="form.show_as" style="width:100%">
                  <el-option label="忙碌" value="busy" />
                  <el-option label="空闲" value="free" />
                  <el-option label="外出" value="out_of_office" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="24">
            <el-col :span="8">
              <el-form-item label="关联账户">
                <el-select v-model="form.what_id" placeholder="选择账户" clearable filterable style="width:100%"
                  @change="onAccountChange">
                  <el-option v-for="acc in accounts" :key="acc.id" :label="acc.name" :value="acc.id" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="关联联系人">
                <el-select v-model="form.who_id" placeholder="选择联系人" clearable filterable style="width:100%">
                  <el-option v-for="c in filteredContacts" :key="c.id" :label="`${c.first_name} ${c.last_name}`" :value="c.id" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="关联商机">
                <el-select v-model="form.what_id_opp" placeholder="选择商机" clearable filterable style="width:100%"
                  @change="onOpportunityChange">
                  <el-option v-for="opp in opportunities" :key="opp.id" :label="opp.name" :value="opp.id" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="拜访目的">
            <el-input v-model="form.purpose" type="textarea" :rows="2" placeholder="请输入拜访目的" />
          </el-form-item>

          <el-form-item label="拜访准备">
            <el-input v-model="form.preparation_notes" type="textarea" :rows="2" placeholder="请输入拜访准备事项" />
          </el-form-item>

          <!-- Edit-only fields -->
          <template v-if="isEdit">
            <el-divider />
            <el-row :gutter="24">
              <el-col :span="8">
                <el-form-item label="拜访结果">
                  <el-select v-model="form.outcome" placeholder="选择结果" clearable style="width:100%">
                    <el-option label="成功" value="success" />
                    <el-option label="一般" value="neutral" />
                    <el-option label="失败" value="failure" />
                    <el-option label="未出席" value="no_show" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="实际开始时间">
                  <el-date-picker v-model="form.actual_start_time" type="datetime" placeholder="签到时间" style="width:100%"
                    value-format="YYYY-MM-DDTHH:mm:ss" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="实际结束时间">
                  <el-date-picker v-model="form.actual_end_time" type="datetime" placeholder="签退时间" style="width:100%"
                    value-format="YYYY-MM-DDTHH:mm:ss" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="拜访纪要">
              <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入拜访纪要" />
            </el-form-item>

            <el-form-item label="下一步计划">
              <el-input v-model="form.next_steps" type="textarea" :rows="2" placeholder="请输入下一步计划" />
            </el-form-item>
          </template>

          <el-form-item>
            <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
            <el-button @click="goBack">取消</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { eventsApi } from '../../api/events'
import { accountsApi } from '../../api/accounts'
import { contactsApi } from '../../api/contacts'
import { opportunitiesApi } from '../../api/opportunities'
import type { Account, Contact, Opportunity } from '../../types/crm'

const route = useRoute()
const router = useRouter()
const formRef = ref()
const loading = ref(false)
const saving = ref(false)
const isEdit = computed(() => !!route.params.id)

const accounts = ref<Account[]>([])
const allContacts = ref<Contact[]>([])
const opportunities = ref<Opportunity[]>([])

const form = reactive({
  subject: '',
  type: 'Visit',
  status: 'planned',
  start_datetime: '',
  end_datetime: '',
  show_as: 'busy',
  what_id: null as number | null,
  what_type: null as string | null,
  what_id_opp: null as number | null,  // helper for opportunity selection
  who_id: null as number | null,
  purpose: '',
  preparation_notes: '',
  description: '',
  outcome: '',
  next_steps: '',
  actual_start_time: '',
  actual_end_time: '',
})

const filteredContacts = computed(() => {
  if (form.what_id) {
    return allContacts.value.filter(c =>
      c.accounts?.some(a => a.account_id === form.what_id)
    )
  }
  return allContacts.value
})

const rules = {
  subject: [{ required: true, message: '请输入拜访主题', trigger: 'blur' }],
  start_datetime: [{ required: true, message: '请选择计划开始时间', trigger: 'change' }],
}

function onAccountChange(val: number | null) {
  if (val) {
    form.what_id = val
    form.what_type = 'account'
    form.who_id = null  // reset contact when account changes
  } else {
    form.what_id = null
    form.what_type = null
  }
}

function onOpportunityChange(val: number | null) {
  if (val) {
    form.what_id = val
    form.what_type = 'opportunity'
    form.what_id_opp = val
  } else {
    form.what_id = null
    form.what_type = null
    form.what_id_opp = null
  }
}

function goBack() {
  router.push(isEdit.value ? `/events/${route.params.id}` : '/events')
}

onMounted(async () => {
  // Load accounts, contacts, opportunities for selectors (each independently)
  try {
    const { data } = await accountsApi.list({ page: 1, page_size: 100 })
    accounts.value = data.items
  } catch (e: any) {
    console.error('加载账户列表失败:', e)
  }

  try {
    const { data } = await contactsApi.list({ page: 1, page_size: 100 })
    allContacts.value = data.items
  } catch (e: any) {
    console.error('加载联系人列表失败:', e)
  }

  try {
    const { data } = await opportunitiesApi.list({ page: 1, page_size: 100 })
    opportunities.value = data.items
  } catch (e: any) {
    console.error('加载商机列表失败:', e)
  }

  // Support query params for quick create from related objects
  if (route.query.what_id && route.query.what_type) {
    form.what_id = route.query.what_id as string
    form.what_type = route.query.what_type as string
    if (form.what_type === 'opportunity') {
      form.what_id_opp = form.what_id
    }
  }
  if (route.query.who_id) {
    form.who_id = route.query.who_id as string
  }

  if (isEdit.value) {
    loading.value = true
    try {
      const { data } = await eventsApi.get(route.params.id as string)
      Object.assign(form, data)
      if (data.what_type === 'opportunity') {
        form.what_id_opp = data.what_id
      }
    } catch {
      ElMessage.error('拜访记录不存在')
      router.push('/events')
    } finally { loading.value = false }
  }
})

async function handleSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    // Prepare payload (remove helper field)
    const payload = { ...form }
    delete (payload as any).what_id_opp

    if (isEdit.value) {
      await eventsApi.update(route.params.id as string, payload)
      ElMessage.success('更新成功')
      router.push(`/events/${route.params.id}`)
    } else {
      const { data } = await eventsApi.create(payload)
      ElMessage.success('创建成功')
      router.push(`/events/${data.id}`)
    }
  } catch {
    ElMessage.error('保存失败')
  } finally { saving.value = false }
}
</script>

<style scoped>
.event-form { max-width: 900px; }
</style>
