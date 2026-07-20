<template>
  <div class="campaign-form-page">
    <h2>{{ isEdit ? '编辑活动' : '新建活动' }}</h2>
    <el-form :model="form" label-width="100px" size="small" style="max-width: 600px; margin-top: 20px">
      <el-form-item label="活动名称" required>
        <el-input v-model="form.name" placeholder="如：2026年度合作伙伴大会" />
      </el-form-item>
      <el-form-item label="类型" required>
        <el-select v-model="form.type" style="width: 100%">
          <el-option label="会议" value="conference" />
          <el-option label="展览" value="exhibition" />
          <el-option label="邮件" value="email" />
          <el-option label="广告" value="ad" />
          <el-option label="其他" value="other" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态" required>
        <el-select v-model="form.status" style="width: 100%">
          <el-option label="规划中" value="planning" />
          <el-option label="进行中" value="in_progress" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
      </el-form-item>
      <el-form-item label="预算">
        <el-input-number v-model="form.budget" :min="0" :step="1000" style="width: 100%">
          <template #prefix>¥</template>
        </el-input-number>
      </el-form-item>
      <el-form-item label="实际成本">
        <el-input-number v-model="form.actual_cost" :min="0" :step="1000" style="width: 100%">
          <template #prefix>¥</template>
        </el-input-number>
      </el-form-item>
      <el-form-item label="开始日期">
        <el-date-picker v-model="form.start_date" type="date" placeholder="选择日期" style="width: 100%" />
      </el-form-item>
      <el-form-item label="结束日期">
        <el-date-picker v-model="form.end_date" type="date" placeholder="选择日期" style="width: 100%" />
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
const campaignId = ref('')

const form = reactive({
  name: '',
  type: 'other',
  status: 'planning',
  budget: null as number | null,
  actual_cost: null as number | null,
  start_date: null as string | null,
  end_date: null as string | null,
  description: '',
})

onMounted(async () => {
  if (route.params.id) {
    isEdit.value = true
    campaignId.value = route.params.id as string
    await loadCampaign()
  }
})

async function loadCampaign() {
  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/campaigns/${campaignId.value}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('Failed to load')
    const data = await res.json()
    form.name = data.name
    form.type = data.type
    form.status = data.status
    form.budget = data.budget
    form.actual_cost = data.actual_cost
    form.start_date = data.start_date
    form.end_date = data.end_date
    form.description = data.description || ''
  } catch (e: any) {
    ElMessage.error('加载失败: ' + (e.message || ''))
  }
}

async function handleSave() {
  if (!form.name) {
    ElMessage.warning('请填写活动名称')
    return
  }

  saving.value = true
  try {
    const token = localStorage.getItem('access_token')
    const body = JSON.stringify({
      name: form.name,
      type: form.type,
      status: form.status,
      budget: form.budget,
      actual_cost: form.actual_cost,
      start_date: form.start_date,
      end_date: form.end_date,
      description: form.description,
    })

    const url = isEdit.value
      ? `/api/campaigns/${campaignId.value}`
      : '/api/campaigns'
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

    ElMessage.success(isEdit.value ? '活动已更新' : '活动已创建')
    router.push('/campaigns')
  } catch (e: any) {
    ElMessage.error('保存失败: ' + (e.message || ''))
  } finally {
    saving.value = false
  }
}

function goBack() {
  router.push('/campaigns')
}
</script>

<style scoped>
.campaign-form-page {
  background: #fff;
  border: 1px solid #dddbda;
  border-radius: 3px;
  padding: 20px;
}

.campaign-form-page h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #080707;
}
</style>