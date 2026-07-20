<template>
  <div class="lead-form-page">
    <h2>{{ isEdit ? '编辑线索' : '新建线索' }}</h2>
    <el-form :model="form" label-width="100px" size="small" style="max-width: 600px; margin-top: 20px">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="名" required>
            <el-input v-model="form.first_name" placeholder="请输入名" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="姓" required>
            <el-input v-model="form.last_name" placeholder="请输入姓" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="公司" required>
        <el-input v-model="form.company" placeholder="请输入公司名称" />
      </el-form-item>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="邮箱">
            <el-input v-model="form.email" placeholder="请输入邮箱" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="电话">
            <el-input v-model="form.phone" placeholder="请输入电话" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="手机">
            <el-input v-model="form.mobile_phone" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="职位">
            <el-input v-model="form.title" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="行业">
            <el-input v-model="form.industry" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="来源">
            <el-select v-model="form.source" style="width: 100%">
              <el-option label="网站" value="Web" />
              <el-option label="电话" value="Phone" />
              <el-option label="推荐" value="Referral" />
              <el-option label="会议" value="Conference" />
              <el-option label="邮件" value="Email" />
              <el-option label="其他" value="Other" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="状态">
        <el-select v-model="form.status" style="width: 100%">
          <el-option label="新线索" value="New" />
          <el-option label="已联系" value="Contacted" />
          <el-option label="已合格" value="Qualified" />
          <el-option label="不合格" value="Unqualified" />
        </el-select>
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" :rows="4" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
        <el-button @click="goBack">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const isEdit = ref(false)
const saving = ref(false)
const leadId = ref('')

const form = reactive({
  first_name: '',
  last_name: '',
  company: '',
  email: '',
  phone: '',
  mobile_phone: '',
  title: '',
  industry: '',
  status: 'New',
  source: 'Other',
  description: '',
})

onMounted(async () => {
  if (route.params.id) {
    isEdit.value = true
    leadId.value = route.params.id as string
    await loadLead()
  }
})

async function loadLead() {
  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/leads/${leadId.value}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('Failed to load')
    const data = await res.json()
    form.first_name = data.first_name
    form.last_name = data.last_name
    form.company = data.company
    form.email = data.email || ''
    form.phone = data.phone || ''
    form.mobile_phone = data.mobile_phone || ''
    form.title = data.title || ''
    form.industry = data.industry || ''
    form.status = data.status
    form.source = data.source
    form.description = data.description || ''
  } catch (e: any) {
    ElMessage.error('加载失败: ' + (e.message || ''))
  }
}

async function handleSave() {
  if (!form.first_name || !form.last_name || !form.company) {
    ElMessage.warning('请填写名、姓和公司')
    return
  }
  saving.value = true
  try {
    const token = localStorage.getItem('access_token')
    const body = JSON.stringify({ ...form })
    const url = isEdit.value ? `/api/leads/${leadId.value}` : '/api/leads'
    const method = isEdit.value ? 'PUT' : 'POST'

    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body,
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Save failed')
    }
    ElMessage.success(isEdit.value ? '线索已更新' : '线索已创建')
    router.push('/leads')
  } catch (e: any) {
    ElMessage.error('保存失败: ' + (e.message || ''))
  } finally {
    saving.value = false
  }
}

function goBack() { router.push('/leads') }
</script>

<style scoped>
.lead-form-page {
  background: #fff;
  border: 1px solid #dddbda;
  border-radius: 3px;
  padding: 20px;
}
.lead-form-page h2 { margin: 0; font-size: 18px; font-weight: 700; color: #080707; }
</style>