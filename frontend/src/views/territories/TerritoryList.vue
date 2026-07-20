<template>
  <div class="territory-split">
    <!-- ── Left: Tree Panel ── -->
    <div class="tree-panel">
      <div class="tree-panel-header">
        <h3 class="tree-panel-title">销售区域</h3>
        <el-button type="primary" size="small" @click="showForm = true; editId = null">
          新建区域
        </el-button>
      </div>
      <el-input
        v-model="treeSearch" placeholder="搜索区域..." size="small" clearable
        style="margin-bottom:8px;"
      />
      <el-tree
        :data="filteredTreeData"
        :props="treeProps"
        node-key="id"
        default-expand-all
        :expand-on-click-node="false"
        highlight-current
        :current-node-key="selectedId"
        @node-click="onNodeClick"
      >
        <template #default="{ node, data }">
          <div class="tree-node">
            <div class="tree-node-info">
              <span class="tree-node-name">{{ data.name }}</span>
              <span class="tree-node-type">{{ typeLabel(data.territory_type) }}</span>
            </div>
            <div class="tree-node-actions">
              <el-button link size="small" type="primary" @click.stop="editNode(data)">编辑</el-button>
              <el-button link size="small" type="danger" @click.stop="deleteNode(data)">删除</el-button>
            </div>
          </div>
        </template>
      </el-tree>
    </div>

    <!-- ── Right: Detail Panel ── -->
    <div class="detail-panel" v-loading="detailLoading">
      <!-- Empty state -->
      <div v-if="!selectedId" class="empty-state">
        <el-icon :size="48" color="#c9c7c5"><map-location /></el-icon>
        <p>请从左侧选择一个销售区域</p>
      </div>

      <!-- Detail -->
      <template v-if="territory">
        <div class="detail-header">
          <h2 class="detail-title">{{ territory.name }}</h2>
          <div class="detail-actions">
            <el-button size="small" @click="editTerritory">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteTerritory">删除</el-button>
          </div>
        </div>

        <div class="highlights-bar">
          <div class="highlight-item">
            <span class="highlight-label">区域编码</span>
            <span class="highlight-value">{{ territory.code || '-' }}</span>
          </div>
          <div class="highlight-item">
            <span class="highlight-label">类型</span>
            <span class="highlight-value">{{ detailTypeLabel }}</span>
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
        </div>

        <el-tabs v-model="activeTab" class="detail-tabs">
          <el-tab-pane label="区域信息" name="info">
            <el-card shadow="never" class="detail-card">
              <el-descriptions :column="2" border size="small">
                <el-descriptions-item label="区域名称">{{ territory.name }}</el-descriptions-item>
                <el-descriptions-item label="区域编码">{{ territory.code || '-' }}</el-descriptions-item>
                <el-descriptions-item label="区域类型">{{ detailTypeLabel }}</el-descriptions-item>
                <el-descriptions-item label="描述" :span="2">{{ territory.description || '-' }}</el-descriptions-item>
              </el-descriptions>
            </el-card>
          </el-tab-pane>

          <el-tab-pane :label="`成员 (${territory.member_count})`" name="members">
            <el-card shadow="never" class="detail-card">
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

          <el-tab-pane :label="`账户 (${territory.account_count})`" name="accounts">
            <el-card shadow="never" class="detail-card">
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

          <el-tab-pane :label="`产品 (${territory.product_count})`" name="products">
            <el-card shadow="never" class="detail-card">
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

          <el-tab-pane label="管道" name="pipeline">
            <el-card shadow="never" class="detail-card">
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
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog v-model="showForm" :title="editId ? '编辑区域' : '新建区域'" width="600px" destroy-on-close>
      <TerritoryForm :territory-id="editId" @saved="onSaved" @cancel="showForm = false" />
    </el-dialog>

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
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MapLocation } from '@element-plus/icons-vue'
import { territoriesApi } from '../../api/territories'
import { authApi } from '../../api/auth'
import { accountsApi } from '../../api/accounts'
import { productsApi } from '../../api/products'
import type { Territory, TerritoryTreeNode, TerritoryMember, TerritoryAccount, TerritoryProduct } from '../../types/territory'
import type { Account, Product } from '../../types/crm'
import type { User } from '../../types/auth'
import TerritoryForm from './TerritoryForm.vue'

// ── Tree ──
const treeData = ref<TerritoryTreeNode[]>([])
const treeProps = { children: 'children', label: 'name' }
const treeSearch = ref('')

const filteredTreeData = computed(() => {
  if (!treeSearch.value) return treeData.value
  const q = treeSearch.value.toLowerCase()
  function filterNodes(nodes: TerritoryTreeNode[]): TerritoryTreeNode[] {
    return nodes.filter(n => {
      const match = n.name.toLowerCase().includes(q) || (n.code || '').toLowerCase().includes(q)
      const filtered = n.children ? filterNodes(n.children) : []
      if (match || filtered.length) {
        n.children = filtered
        return true
      }
      return false
    })
  }
  return filterNodes(JSON.parse(JSON.stringify(treeData.value)))
})

// ── Selected territory ──
const selectedId = ref<string | null>(null)
const territory = ref<Territory | null>(null)
const detailLoading = ref(false)
const activeTab = ref('info')

// ── Related data ──
const members = ref<TerritoryMember[]>([])
const territoryAccounts = ref<TerritoryAccount[]>([])
const territoryProducts = ref<TerritoryProduct[]>([])
const pipelineData = ref<any[]>([])
const allUsers = ref<User[]>([])
const allAccounts = ref<Account[]>([])
const allProducts = ref<Product[]>([])

// ── Dialogs ──
const showForm = ref(false)
const editId = ref<string | null>(null)
const showAddMember = ref(false)
const showAddAccount = ref(false)
const showAddProduct = ref(false)
const savingMember = ref(false)
const savingAccount = ref(false)
const savingProduct = ref(false)
const newMember = ref({ user_id: null as string | null, role: 'member' })
const newAccount = ref({ account_id: null as string | null })
const newProduct = ref({ product_id: null as string | null, price: null as number | null })

// ── Helpers ──
function typeLabel(type: string): string {
  const map: Record<string, string> = { region: '大区', district: '区域', branch: '分部', custom: '自定义' }
  return map[type] || type
}

const detailTypeLabel = computed(() => typeLabel(territory.value?.territory_type || ''))

// ── Tree actions ──
async function fetchTree() {
  try {
    const { data } = await territoriesApi.getTree()
    treeData.value = data
  } catch { /* ignore */ }
}

function onNodeClick(data: TerritoryTreeNode) {
  selectedId.value = data.id.toString()
}

function editNode(data: TerritoryTreeNode) {
  editId.value = data.id.toString()
  showForm.value = true
}

async function deleteNode(data: TerritoryTreeNode) {
  try {
    await ElMessageBox.confirm(`确定删除区域 "${data.name}" 吗？`, '确认删除', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
    await territoriesApi.delete(data.id.toString())
    ElMessage.success('删除成功')
    if (selectedId.value === data.id.toString()) {
      selectedId.value = null
      territory.value = null
    }
    await fetchTree()
  } catch { /* cancelled */ }
}

function onSaved() {
  showForm.value = false
  editId.value = null
  fetchTree()
}

// ── Detail loading ──
async function fetchTerritoryDetail(id: string) {
  detailLoading.value = true
  try {
    const { data } = await territoriesApi.get(id)
    territory.value = data
  } catch {
    ElMessage.error('区域不存在')
    territory.value = null
    selectedId.value = null
  } finally {
    detailLoading.value = false
  }
}

async function fetchMembers(id: string) {
  try { const { data } = await territoriesApi.listMembers(id); members.value = data } catch { /* ignore */ }
}
async function fetchTerritoryAccounts(id: string) {
  try { const { data } = await territoriesApi.listAccounts(id); territoryAccounts.value = data } catch { /* ignore */ }
}
async function fetchTerritoryProducts(id: string) {
  try { const { data } = await territoriesApi.listProducts(id); territoryProducts.value = data } catch { /* ignore */ }
}
async function fetchTerritoryPipeline(id: string) {
  try { const { data } = await territoriesApi.getPipeline(id); pipelineData.value = data.stages || [] } catch { /* ignore */ }
}

async function loadAllSelectors() {
  try {
    const [u, a, p] = await Promise.all([
      authApi.listUsers(),
      accountsApi.list({ page: 1, page_size: 100 }),
      productsApi.list({ page: 1, page_size: 100 }),
    ])
    allUsers.value = u.data.items
    allAccounts.value = a.data.items
    allProducts.value = p.data.items
  } catch { /* ignore */ }
}

watch(selectedId, async (id) => {
  if (!id) return
  await fetchTerritoryDetail(id)
  if (territory.value) {
    await Promise.all([
      fetchMembers(id),
      fetchTerritoryAccounts(id),
      fetchTerritoryProducts(id),
      fetchTerritoryPipeline(id),
    ])
  }
}, { immediate: false })

// ── Detail actions ──
function editTerritory() {
  if (!selectedId.value) return
  editId.value = selectedId.value
  showForm.value = true
}

async function deleteTerritory() {
  if (!territory.value) return
  try {
    await ElMessageBox.confirm(`确定删除区域 "${territory.value.name}" 吗？`, '确认删除', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
    await territoriesApi.delete(territory.value.id)
    ElMessage.success('删除成功')
    selectedId.value = null
    territory.value = null
    await fetchTree()
  } catch { /* cancelled */ }
}

// Member actions
async function addMember() {
  if (!newMember.value.user_id || !selectedId.value) return
  savingMember.value = true
  try {
    await territoriesApi.addMember(selectedId.value, { user_id: newMember.value.user_id, role: newMember.value.role })
    ElMessage.success('成员添加成功')
    showAddMember.value = false
    newMember.value = { user_id: null, role: 'member' }
    await fetchMembers(selectedId.value)
    await fetchTerritoryDetail(selectedId.value)
  } catch { ElMessage.error('添加失败') }
  finally { savingMember.value = false }
}

async function removeMember(row: TerritoryMember) {
  if (!selectedId.value) return
  try {
    await territoriesApi.removeMember(selectedId.value, row.id)
    ElMessage.success('成员已移除')
    await fetchMembers(selectedId.value)
    await fetchTerritoryDetail(selectedId.value)
  } catch { ElMessage.error('移除失败') }
}

// Account actions
async function addAccount() {
  if (!newAccount.value.account_id || !selectedId.value) return
  savingAccount.value = true
  try {
    await territoriesApi.addAccount(selectedId.value, { account_id: newAccount.value.account_id })
    ElMessage.success('账户关联成功')
    showAddAccount.value = false
    newAccount.value = { account_id: null }
    await fetchTerritoryAccounts(selectedId.value)
    await fetchTerritoryDetail(selectedId.value)
  } catch { ElMessage.error('关联失败') }
  finally { savingAccount.value = false }
}

async function removeAccount(row: TerritoryAccount) {
  if (!selectedId.value) return
  try {
    await territoriesApi.removeAccount(selectedId.value, row.account_id)
    ElMessage.success('账户已解除关联')
    await fetchTerritoryAccounts(selectedId.value)
    await fetchTerritoryDetail(selectedId.value)
  } catch { ElMessage.error('移除失败') }
}

// Product actions
async function addProduct() {
  if (!newProduct.value.product_id || !selectedId.value) return
  savingProduct.value = true
  try {
    await territoriesApi.addProduct(selectedId.value, { product_id: newProduct.value.product_id, price: newProduct.value.price })
    ElMessage.success('产品添加成功')
    showAddProduct.value = false
    newProduct.value = { product_id: null, price: null }
    await fetchTerritoryProducts(selectedId.value)
    await fetchTerritoryDetail(selectedId.value)
  } catch { ElMessage.error('添加失败') }
  finally { savingProduct.value = false }
}

async function removeProduct(row: TerritoryProduct) {
  if (!selectedId.value) return
  try {
    await territoriesApi.removeProduct(selectedId.value, row.product_id)
    ElMessage.success('产品已移除')
    await fetchTerritoryProducts(selectedId.value)
    await fetchTerritoryDetail(selectedId.value)
  } catch { ElMessage.error('移除失败') }
}

onMounted(async () => {
  await fetchTree()
  await loadAllSelectors()
})
</script>

<style scoped>
.territory-split {
  display: flex;
  height: calc(100vh - 130px);
  gap: 16px;
}

/* ── Left Tree Panel ── */
.tree-panel {
  width: 300px;
  min-width: 300px;
  background: #fff;
  border: 1px solid #dddbda;
  border-radius: 3px;
  padding: 12px;
  overflow-y: auto;
}

.tree-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.tree-panel-title {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2px 0;
  width: 100%;
}

.tree-node-info {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

.tree-node-name {
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tree-node-type {
  font-size: 10px;
  color: #fff;
  background: #1589ee;
  border-radius: 3px;
  padding: 1px 5px;
  white-space: nowrap;
}

.tree-node-actions {
  opacity: 0;
  transition: opacity 0.15s;
  display: flex;
  gap: 2px;
}

.tree-node:hover .tree-node-actions {
  opacity: 1;
}

/* ── Right Detail Panel ── */
.detail-panel {
  flex: 1;
  background: #fff;
  border: 1px solid #dddbda;
  border-radius: 3px;
  padding: 16px;
  overflow-y: auto;
  min-height: 400px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #706e6b;
  gap: 12px;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.detail-title {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.detail-actions {
  display: flex;
  gap: 8px;
}

.highlights-bar {
  display: flex;
  background: #f8f9fb;
  border: 1px solid #dddbda;
  border-radius: 3px;
  margin-bottom: 12px;
  overflow: hidden;
}

.highlight-item {
  flex: 1;
  padding: 10px 14px;
  border-right: 1px solid #dddbda;
}

.highlight-item:last-child {
  border-right: none;
}

.highlight-label {
  display: block;
  font-size: 11px;
  color: #706e6b;
  margin-bottom: 3px;
}

.highlight-value {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.detail-tabs {
  margin-top: 4px;
}

.detail-card {
  margin-bottom: 12px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.section-header h3 {
  margin: 0;
  font-size: 14px;
  color: #333;
}

.text-muted {
  color: #999;
  font-style: italic;
}
</style>
