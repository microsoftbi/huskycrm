<template>
  <div class="account-form" v-loading="loading">
    <div class="sf-page-header">
      <el-button @click="goBack" icon="arrow-left" text>返回</el-button>
      <h2 class="sf-page-title">{{ isEdit ? '编辑账户' : '新建账户' }}</h2>
    </div>

    <div class="sf-card">
      <div class="sf-card-body">
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" size="small">
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="账户名称" prop="name">
                <el-input v-model="form.name" placeholder="请输入账户名称" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="行业">
                <el-input v-model="form.industry" placeholder="请输入行业" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="电话">
                <el-input v-model="form.phone" placeholder="请输入电话" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="邮箱">
                <el-input v-model="form.email" placeholder="请输入邮箱" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="网站">
                <el-input v-model="form.website" placeholder="https://" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-divider content-position="left" style="margin: 12px 0;">账单地址</el-divider>

          <el-row :gutter="24">
            <el-col :span="24">
              <el-form-item label="街道">
                <el-input v-model="form.billing_street" placeholder="街道地址" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="8">
              <el-form-item label="城市">
                <el-input v-model="form.billing_city" placeholder="城市" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="省份">
                <el-input v-model="form.billing_state" placeholder="省份" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="邮编">
                <el-input v-model="form.billing_zip" placeholder="邮编" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="国家">
                <el-input v-model="form.billing_country" placeholder="国家" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="描述">
            <el-input v-model="form.description" type="textarea" :rows="3" placeholder="备注信息" />
          </el-form-item>

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
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { accountsApi } from '../../api/accounts'

const route = useRoute()
const router = useRouter()
const formRef = ref()
const loading = ref(false)
const saving = ref(false)

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  name: '', industry: '', phone: '', website: '', email: '',
  billing_street: '', billing_city: '', billing_state: '', billing_zip: '', billing_country: '',
  description: '',
})

const rules = {
  name: [{ required: true, message: '请输入账户名称', trigger: 'blur' }],
}

function goBack() {
  router.push(isEdit.value ? `/accounts/${route.params.id}` : '/accounts')
}

onMounted(async () => {
  if (isEdit.value) {
    loading.value = true
    try {
      const { data } = await accountsApi.get(route.params.id as string)
      Object.assign(form, data)
    } catch {
      ElMessage.error('账户不存在')
      router.push('/accounts')
    } finally {
      loading.value = false
    }
  }
})

async function handleSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value) {
      await accountsApi.update(route.params.id as string, form)
      ElMessage.success('更新成功')
      router.push(`/accounts/${route.params.id}`)
    } else {
      const { data } = await accountsApi.create(form)
      ElMessage.success('创建成功')
      router.push(`/accounts/${data.id}`)
    }
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.account-form {
  max-width: 900px;
}
</style>
