<template>
  <div class="territory-detail" v-loading="loading">
    <div class="sf-page-header">
      <el-button @click="goBack" icon="arrow-left" text>返回</el-button>
      <h2 class="sf-page-title" v-if="territory">{{ territory.name }}</h2>
    </div>

    <template v-if="territory">
      <!-- Highlights Panel -->
      <div class="highlights-bar">
        <div class="highlight-item">
          <span class="highlight-label">区域编码</span>
          <span class="highlight-value">{{ territory.code || '-' }}</span>
        </div>
        <div class="highlight-item">
          <span class="highlight-label">类型</span>
          <span class="highlight-value">{{ typeLabel }}</span>
        </div>
        <div class="highlight-item">
          <span class="highlight-label">成员</span>
          <span class="highlight-value">{{ territory.member_count }}</span>
        </div>
        <div class="highlight-item">
          <span class="highlight-label">账户</span>
          <span class="highlight-value">{{ territory.account_count }}</span>
        </div>
        <div class="highlight-item">
          <span class="highlight-label">产品</span>
          <span class="highlight-value">{{ territory.product_count }}</span>
        </div>
        <div class="highlight-item actions">
          <el-button size="small" @click="editTerritory">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteTerritory">删除</el-button>
        </div>
      </div>

      <!-- Tabs -->
      <el-tabs v-model="activeTab">
        <el-tab-pane label="区域信息" name="info">
          <el-card shadow="hover">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="区域名称">{{ territory.name }}</el-descriptions-item>
              <el-descriptions-item label="区域编码">{{ territory.code || '-' }}</el-descriptions-item>
              <el-descriptions-item label="区域类型">{{ typeLabel }}</el-descriptions-item>
              <el-descriptions-item label="上级区域">{{ parentName || '-' }}</el-descriptions-item>
              <el-descriptions-item label="描述" :span="2">{{ territory.description || '-' }}</el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-tab-pane>

        <!-- Members Tab -->
        <el-tab-pane :label="`成员 (${territory.member_count})`" name="members">
          <el-card shadow="hover">
            <div class="section-header">
              <h3>区域成员</h3>
              <el-button type="primary" size="small" @click="showAddMember = true">添加成员</el-button>
            </div>
            <el-table :data="members" border size="small" style="width:100%">
              <el-table-column label="用户名" prop="username" />
              <el-table-column label="显示名" prop="display_name" />
              <el-table-column label="角色">
                <template #default="{ row }">
                  <el-tag :type="row.role === 'manager' ? 'warning' : 'info'" size="small">
                    {{ row.role === 'manager' ? '负责人' : '成员' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="分配时间" prop="assigned_at" width="180" />
              <el-table-column label="操作" width="100" align="center">
                <template #default="{ row }">
                  <el-button type="danger" link size="small" @click="removeMember(row)">移除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-tab-pane>

        <!-- Accounts Tab -->
        <el-tab-pane :label="`账户 (${territory.account_count})`" name="accounts">
          <el-card shadow="hover">
            <div class="section-header">
              <h3>关联账户</h3>
              <el-button type="primary" size="small" @click="showAddAccount = true">关联账户</el-button>
            </div>
            <el-table :data="territoryAccounts" border size="small" style="width:100%">
              <el-table-column label="账户名称" prop="account_name" />
              <el-table-column label="关联时间" prop="assigned_at" width="180" />
              <el-table-column label="操作" width="100" align="center">
                <template #default="{ row }">
                  <el-button type="danger" link size="small" @click="removeAccount(row)">移除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-tab-pane>

        <!-- Products Tab -->
        <el-tab-pane :label="`产品 (${territory.product_count})`" name="products">
          <el-card shadow="hover">
            <div class="section-header">
              <h3>区域产品</h3>
              <el-button type="primary" size="small" @click="showAddProduct = true">添加产品</el-button>
            </div>
            <el-table :data="territoryProducts" border size="small" style="width:100%">
              <el-table-column label="产品名称" prop="product_name" />
              <el-table-column label="产品编码" prop="product_code" width="120" />
              <el-table-column label="默认价格" width="150">
                <template #default="{ row }">
                  ¥{{ (row.default_price || 0).toFixed(2) }}
                </template>
              </el-table-column>
              <el-table-column label="区域价格" width="150">
                <template #default="{ row }">
                  <span v-if="row.price != null">¥{{ row.price.toFixed(2) }}</span>
                  <span v-else class="text-muted">使用默认</span>
                </template>
              </el-table-column>
              <el-table-column label="状态" width="80">
                <template #default="{ row }">
                  <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
                    {{ row.is_active ? '启用' : '停用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="{ row }">
                  <el-button type="danger" link size="small" @click="removeProduct(row)">移除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-tab-pane>

        <!-- Pipeline Tab -->
        <el-tab-pane label="管道" name="pipeline">
          <el-card shadow="hover">
            <h3>区域管道</h3>
            <el-table :data="pipelineData" border size="small" style="width:100%">
              <el-table-column label="阶段" prop="stage.name" />
              <el-table-column label="机会数" prop="count" width="100" align="center" />
              <el-table-column label="总额" width="200" align="right">
                <template #default="{ row }">
                  ¥{{ (row.total_amount || 0).toLocaleString() }}
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </template>

    <!-- Add Member Dialog -->
    <el-dialog v-model="showAddMember" title="添加成员" width="400px">
      <el-form label-position="top">
        <el-form-item label="选择用户">
          <el-select v-model="newMember.user_id" placeholder="选择用户" filterable style="width:100%">
            <el-option v-for="u in allUsers" :key="u.id" :label="u.display_name || u.username" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="newMember.role" style="width:100%">
            <el-option label="成员" value="member" />
            <el-option label="负责人" value="manager" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddMember = false">取消</el-button>
        <el-button type="primary" :loading="savingMember" @click="addMember">确定</el-button>
      </template>
    </el-dialog>

    <!-- Add Account Dialog -->
    <el-dialog v-model="showAddAccount" title="关联账户" width="400px">
      <el-form label-position="top">
        <el-form-item label="选择账户">
          <el-select v-model="newAccount.account_id" placeholder="选择账户" filterable style="width:100%">
            <el-option v-for="a in allAccounts" :key="a.id" :label="a.name" :value="a.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddAccount = false">取消</el-button>
        <el-button type="primary" :loading="savingAccount" @click="addAccount">确定</el-button>
      </template>
    </el-dialog>

    <!-- Add Product Dialog -->
    <el-dialog v-model="showAddProduct" title="添加产品" width="400px">
      <el-form label-position="top">
        <el-form-item label="选择产品">
          <el-select v-model="newProduct.product_id" placeholder="选择产品" filterable style="width:100%">
            <el-option v-for="p in allProducts" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="区域价格（留空使用默认）">
          <el-input-number v-model="newProduct.price" :min="0" :precision="2" style="width:100%" placeholder="留空则使用产品默认价格" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddProduct = false">取消</el-button>
        <el-button type="primary" :loading="savingProduct" @click="addProduct">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { territoriesApi } from '../../api/territories'
import { authApi } from '../../api/auth'
import { accountsApi } from '../../api/accounts'
import { productsApi } from '../../api/products'
import type { Territory, TerritoryMember, TerritoryAccount, TerritoryProduct } from '../../types/territory'
import type { Account, Product } from '../../types/crm'
import type { User } from '../../types/auth'

const route = useRoute()
const router = useRouter()
const territory = ref<Territory | null>(null)
const loading = ref(false)
const activeTab = ref('info')

// Related data
const members = ref<TerritoryMember[]>([])
const territoryAccounts = ref<TerritoryAccount[]>([])
const territoryProducts = ref<TerritoryProduct[]>([])
const pipelineData = ref<any[]>([])
const allUsers = ref<User[]>([])
const allAccounts = ref<Account[]>([])
const allProducts = ref<Product[]>([])

// Dialogs
const showAddMember = ref(false)
const showAddAccount = ref(false)
const showAddProduct = ref(false)
const savingMember = ref(false)
const savingAccount = ref(false)
const savingProduct = ref(false)
const newMember = ref({ user_id: null as number | null, role: 'member' })
const newAccount = ref({ account_id: null as number | null })
const newProduct = ref({ product_id: null as number | null, price: null as number | null })

const typeLabel = computed(() => {
  const map: Record<string, string> = { region: '大区', district: '区域', branch: '分部', custom: '自定义' }
  return map[territory.value?.territory_type || ''] || territory.value?.territory_type || '-'
})

const parentName = computed(() => {
  // Parent info is not loaded in the flat response, show placeholder
  return '-'
})

function goBack() {
  router.push('/admin/territories')
}

async function fetchTerritory() {
  loading.value = true
  try {
    const { data } = await territoriesApi.get(route.params.id as string)
    territory.value = data
  } catch {
    ElMessage.error('区域不存在')
    router.push('/admin/territories')
  } finally {
    loading.value = false
  }
}

async function fetchMembers() {
  try {
    const { data } = await territoriesApi.listMembers(route.params.id as string)
    members.value = data
  } catch { /* ignore */ }
}

async function fetchAccounts() {
  try {
    const { data } = await territoriesApi.listAccounts(route.params.id as string)
    territoryAccounts.value = data
  } catch { /* ignore */ }
}

async function fetchProducts() {
  try {
    const { data } = await territoriesApi.listProducts(route.params.id as string)
    territoryProducts.value = data
  } catch { /* ignore */ }
}

async function fetchPipeline() {
  try {
    const { data } = await territoriesApi.getPipeline(route.params.id as string)
    pipelineData.value = data.stages || []
  } catch { /* ignore */ }
}

async function fetchAllUsers() {
  try {
    const { data } = await authApi.listUsers()
    allUsers.value = data
  } catch { /* ignore */ }
}

async function fetchAllAccounts() {
  try {
    const { data } = await accountsApi.list({ page: 1, page_size: 100 })
    allAccounts.value = data.items
  } catch { /* ignore */ }
}

async function fetchAllProducts() {
  try {
    const { data } = await productsApi.list({ page: 1, page_size: 100 })
    allProducts.value = data.items
  } catch { /* ignore */ }
}

function editTerritory() {
  router.push(`/admin/territories/${route.params.id}/edit`)
}

async function deleteTerritory() {
  if (!territory.value) return
  try {
    await ElMessageBox.confirm(`确定删除区域 "${territory.value.name}" 吗？`, '确认删除', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
    await territoriesApi.delete(territory.value.id)
    ElMessage.success('删除成功')
    router.push('/admin/territories')
  } catch { /* cancelled */ }
}

// Member actions
async function addMember() {
  if (!newMember.value.user_id) return
  savingMember.value = true
  try {
    await territoriesApi.addMember(route.params.id as string, {
      user_id: newMember.value.user_id,
      role: newMember.value.role,
    })
    ElMessage.success('成员添加成功')
    showAddMember.value = false
    newMember.value = { user_id: null, role: 'member' }
    await fetchMembers()
    await fetchTerritory()
  } catch {
    ElMessage.error('添加失败')
  } finally {
    savingMember.value = false
  }
}

async function removeMember(row: TerritoryMember) {
  try {
    await territoriesApi.removeMember(route.params.id as string, row.id)
    ElMessage.success('成员已移除')
    await fetchMembers()
    await fetchTerritory()
  } catch {
    ElMessage.error('移除失败')
  }
}

// Account actions
async function addAccount() {
  if (!newAccount.value.account_id) return
  savingAccount.value = true
  try {
    await territoriesApi.addAccount(route.params.id as string, {
      account_id: newAccount.value.account_id,
    })
    ElMessage.success('账户关联成功')
    showAddAccount.value = false
    newAccount.value = { account_id: null }
    await fetchAccounts()
    await fetchTerritory()
  } catch {
    ElMessage.error('关联失败')
  } finally {
    savingAccount.value = false
  }
}

async function removeAccount(row: TerritoryAccount) {
  try {
    await territoriesApi.removeAccount(route.params.id as string, row.account_id)
    ElMessage.success('账户已解除关联')
    await fetchAccounts()
    await fetchTerritory()
  } catch {
    ElMessage.error('移除失败')
  }
}

// Product actions
async function addProduct() {
  if (!newProduct.value.product_id) return
  savingProduct.value = true
  try {
    await territoriesApi.addProduct(route.params.id as string, {
      product_id: newProduct.value.product_id,
      price: newProduct.value.price,
    })
    ElMessage.success('产品添加成功')
    showAddProduct.value = false
    newProduct.value = { product_id: null, price: null }
    await fetchProducts()
    await fetchTerritory()
  } catch {
    ElMessage.error('添加失败')
  } finally {
    savingProduct.value = false
  }
}

async function removeProduct(row: TerritoryProduct) {
  try {
    await territoriesApi.removeProduct(route.params.id as string, row.product_id)
    ElMessage.success('产品已移除')
    await fetchProducts()
    await fetchTerritory()
  } catch {
    ElMessage.error('移除失败')
  }
}

onMounted(async () => {
  await fetchTerritory()
  if (territory.value) {
    await Promise.all([
      fetchMembers(),
      fetchAccounts(),
      fetchProducts(),
      fetchPipeline(),
      fetchAllUsers(),
      fetchAllAccounts(),
      fetchAllProducts(),
    ])
  }
})
</script>

<style scoped>
.territory-detail { max-width: 960px; }
.sf-page-header {
  display: flex; align-items: center; gap: 12px; margin-bottom: 20px;
}
.sf-page-title { margin: 0; font-size: 22px; color: #333; }

.highlights-bar {
  display: flex; background: #fff; border: 1px solid #dddbda; border-radius: 3px;
  margin-bottom: 12px; overflow: hidden;
}
.highlight-item {
  flex: 1; padding: 12px 16px; border-right: 1px solid #dddbda;
}
.highlight-item:last-child { border-right: none; }
.highlight-item.actions { flex: 0 0 auto; display: flex; align-items: center; gap: 8px; }
.highlight-label { display: block; font-size: 11px; color: #706e6b; margin-bottom: 4px; }
.highlight-value { font-size: 16px; font-weight: 600; color: #333; }

.section-header {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;
}
.section-header h3 { margin: 0; font-size: 15px; color: #333; }
.text-muted { color: #999; font-style: italic; }
</style>
