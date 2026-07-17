<template>
  <div class="contact-form" v-loading="loading">
    <div class="sf-page-header">
      <el-button @click="goBack" icon="arrow-left" text>返回</el-button>
      <h2 class="sf-page-title">{{ isEdit ? '编辑联系人' : '新建联系人' }}</h2>
    </div>

    <div class="sf-card">
      <div class="sf-card-body">
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" size="small">
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="名字" prop="first_name">
                <el-input v-model="form.first_name" placeholder="请输入名字" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="姓氏" prop="last_name">
                <el-input v-model="form.last_name" placeholder="请输入姓氏" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="邮箱"><el-input v-model="form.email" placeholder="请输入邮箱" /></el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="电话"><el-input v-model="form.phone" placeholder="请输入电话" /></el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="手机"><el-input v-model="form.mobile_phone" placeholder="请输入手机" /></el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="职位"><el-input v-model="form.title" placeholder="请输入职位" /></el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="部门"><el-input v-model="form.department" placeholder="请输入部门" /></el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="关联账户">
                <el-select v-model="form.account_id" placeholder="选择账户" clearable filterable style="width:100%">
                  <el-option v-for="acc in accounts" :key="acc.id" :label="acc.name" :value="acc.id" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
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
import { contactsApi } from '../../api/contacts'
import { accountsApi } from '../../api/accounts'
import type { Account } from '../../types/crm'

const route = useRoute()
const router = useRouter()
const formRef = ref()
const loading = ref(false)
const saving = ref(false)
const accounts = ref<Account[]>([])

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  first_name: '', last_name: '', email: '', phone: '', mobile_phone: '',
  title: '', department: '', account_id: undefined as string | undefined,
})

const rules = {
  first_name: [{ required: true, message: '请输入名字', trigger: 'blur' }],
  last_name: [{ required: true, message: '请输入姓氏', trigger: 'blur' }],
}

function goBack() {
  router.push(isEdit.value ? `/contacts/${route.params.id}` : '/contacts')
}

onMounted(async () => {
  // Support account_id from query parameter (when creating from account detail)
  if (route.query.account_id) {
    form.account_id = route.query.account_id as string
  }

  try {
    const { data } = await accountsApi.list({ page: 1, page_size: 100 })
    accounts.value = data.items
  } catch { /* ignore */ }

  if (isEdit.value) {
    loading.value = true
    try {
      const { data } = await contactsApi.get(route.params.id as string)
      Object.assign(form, data)
    } catch {
      ElMessage.error('联系人不存在')
      router.push('/contacts')
    } finally { loading.value = false }
  }
})

async function handleSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value) {
      await contactsApi.update(route.params.id as string, form)
      ElMessage.success('更新成功')
      router.push(`/contacts/${route.params.id}`)
    } else {
      const { data } = await contactsApi.create(form)
      ElMessage.success('创建成功')
      router.push(`/contacts/${data.id}`)
    }
  } catch { ElMessage.error('保存失败') }
  finally { saving.value = false }
}
</script>

<style scoped>
.contact-form { max-width: 900px; }
</style>
