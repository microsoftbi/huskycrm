<template>
  <div class="product-detail" v-loading="loading">
    <div class="sf-page-header">
      <el-button @click="$router.push('/products')" icon="arrow-left" text>返回</el-button>
      <h2 class="sf-page-title">产品详情</h2>
    </div>

    <template v-if="product">
      <div class="sf-record-header">
        <div class="sf-record-icon">
          <el-icon :size="20"><box /></el-icon>
        </div>
        <div class="sf-record-name">{{ product.name }}</div>
        <div class="sf-record-actions">
          <el-button type="primary" size="small" icon="edit" @click="$router.push(`/products/${product.id}/edit`)">编辑</el-button>
          <el-button size="small" type="danger" plain icon="delete" @click="handleDelete">删除</el-button>
        </div>
      </div>

      <RecordSection title="产品信息" :fields="basicFields" />
      <RecordSection title="定价信息" :fields="pricingFields" />
      <RecordSection title="系统信息" :fields="systemFields" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { productsApi } from '../../api/products'
import type { Product } from '../../types/crm'
import RecordHeader from '../../components/record/RecordHeader.vue'
import RecordSection from '../../components/record/RecordSection.vue'

const route = useRoute()
const router = useRouter()
const product = ref<Product | null>(null)
const loading = ref(false)

const basicFields = computed(() => [
  { label: '产品名称', apiName: 'name', value: product.value?.name },
  { label: '产品编码', apiName: 'product_code', value: product.value?.product_code },
  { label: '分类', apiName: 'category', value: product.value?.category },
  { label: '状态', apiName: 'is_active', value: product.value?.is_active ? '启用' : '停用' },
  { label: '描述', apiName: 'description', value: product.value?.description },
])

const pricingFields = computed(() => [
  { label: '售价', apiName: 'price', value: product.value?.price ? `¥${product.value.price.toLocaleString()}` : '-' },
  { label: '成本', apiName: 'cost', value: product.value?.cost ? `¥${product.value.cost.toLocaleString()}` : '-' },
])

const systemFields = computed(() => [
  { label: '创建时间', apiName: 'created_at', value: product.value?.created_at },
  { label: '更新时间', apiName: 'updated_at', value: product.value?.updated_at },
])

async function fetchProduct() {
  loading.value = true
  try {
    const { data } = await productsApi.get(route.params.id as string)
    product.value = data
  } catch {
    ElMessage.error('产品不存在')
    router.push('/products')
  } finally { loading.value = false }
}

async function handleDelete() {
  if (!product.value) return
  try {
    await ElMessageBox.confirm(`确定删除产品 "${product.value.name}" 吗？`, '确认删除', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
    await productsApi.delete(product.value.id)
    ElMessage.success('删除成功')
    router.push('/products')
  } catch { /* cancelled */ }
}

onMounted(fetchProduct)
</script>

<style scoped>
.product-detail { max-width: 900px; }
</style>
