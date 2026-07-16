<template>
  <div class="product-list">
    <div class="sf-page-header">
      <h2 class="sf-page-title">产品</h2>
      <div class="sf-page-actions">
        <router-link to="/products/new">
          <el-button type="primary" size="small" icon="plus">新建产品</el-button>
        </router-link>
      </div>
    </div>

    <div class="sf-card">
      <div class="sf-filter-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索产品名称..."
          clearable
          size="small"
          @clear="fetchProducts"
          @keyup.enter="fetchProducts"
        >
          <template #prefix><el-icon><search /></el-icon></template>
        </el-input>
      </div>

      <el-table :data="products" stripe v-loading="loading" class="sf-table-compact" size="small" style="width:100%">
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="name" label="名称" min-width="180">
          <template #default="{ row }">
            <router-link :to="`/products/${row.id}`">
              <el-link type="primary">{{ row.name }}</el-link>
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="product_code" label="产品编码" width="140" />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column label="价格" width="120">
          <template #default="{ row }">¥{{ (row.price || 0).toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/products/${row.id}`)">查看</el-button>
            <el-button size="small" type="danger" plain @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="padding:10px 14px;display:flex;justify-content:flex-end;border-top:1px solid #dddbda;">
        <el-pagination
          v-model:current-page="page" v-model:page-size="pageSize"
          :total="total" :page-sizes="[10,20,50]"
          layout="total, sizes, prev, pager, next"
          size="small" @change="fetchProducts"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { productsApi } from '../../api/products'
import type { Product } from '../../types/crm'

const products = ref<Product[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const searchQuery = ref('')

async function fetchProducts() {
  loading.value = true
  try {
    const { data } = await productsApi.list({
      page: page.value, page_size: pageSize.value, search: searchQuery.value,
    })
    products.value = data.items
    total.value = data.total
  } finally { loading.value = false }
}

async function handleDelete(row: Product) {
  try {
    await ElMessageBox.confirm(`确定删除产品 "${row.name}" 吗？`, '确认删除', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
    await productsApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchProducts()
  } catch { /* cancelled */ }
}

onMounted(fetchProducts)
</script>

<style scoped>
.product-list { max-width: 1200px; }
</style>
