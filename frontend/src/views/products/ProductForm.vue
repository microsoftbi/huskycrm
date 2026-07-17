<template>
  <div class="product-form" v-loading="loading">
    <div class="sf-page-header">
      <el-button @click="goBack" icon="arrow-left" text>返回</el-button>
      <h2 class="sf-page-title">{{ isEdit ? '编辑产品' : '新建产品' }}</h2>
    </div>

    <div class="sf-card">
      <div class="sf-card-body">
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" size="small">
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="产品名称" prop="name">
                <el-input v-model="form.name" placeholder="请输入产品名称" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="产品编码">
                <el-input v-model="form.product_code" placeholder="请输入产品编码" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="售价">
                <el-input-number v-model="form.price" :min="0" :precision="2" style="width:100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="成本">
                <el-input-number v-model="form.cost" :min="0" :precision="2" style="width:100%" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="分类">
                <el-input v-model="form.category" placeholder="请输入分类" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="状态">
                <el-switch v-model="form.is_active" active-text="启用" inactive-text="停用" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="描述">
            <el-input v-model="form.description" type="textarea" :rows="3" placeholder="产品描述" />
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
import { productsApi } from '../../api/products'

const route = useRoute()
const router = useRouter()
const formRef = ref()
const loading = ref(false)
const saving = ref(false)

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  name: '',
  product_code: '',
  description: '',
  price: 0,
  cost: 0,
  category: '',
  is_active: true,
})

const rules = {
  name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
}

function goBack() {
  router.push(isEdit.value ? `/products/${route.params.id}` : '/products')
}

onMounted(async () => {
  if (isEdit.value) {
    loading.value = true
    try {
      const { data } = await productsApi.get(route.params.id as string)
      Object.assign(form, data)
    } catch {
      ElMessage.error('产品不存在')
      router.push('/products')
    } finally { loading.value = false }
  }
})

async function handleSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value) {
      await productsApi.update(route.params.id as string, form)
      ElMessage.success('更新成功')
      router.push(`/products/${route.params.id}`)
    } else {
      const { data } = await productsApi.create(form)
      ElMessage.success('创建成功')
      router.push(`/products/${data.id}`)
    }
  } catch { ElMessage.error('保存失败') }
  finally { saving.value = false }
}
</script>

<style scoped>
.product-form { max-width: 900px; }
</style>
