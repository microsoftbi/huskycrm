<template>
  <div class="opportunity-form" v-loading="loading">
    <div class="form-header">
      <el-button @click="goBack" icon="arrow-left" text>返回</el-button>
      <h2 class="page-title">{{ isEdit ? '编辑机会' : '新建机会' }}</h2>
    </div>

    <el-card shadow="hover">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="机会名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入机会名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关联账户">
              <el-select v-model="form.account_id" placeholder="选择账户" clearable filterable style="width:100%">
                <el-option v-for="acc in accounts" :key="acc.id" :label="acc.name" :value="acc.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="金额 (元)">
              <el-input-number v-model="form.amount" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="销售阶段" prop="stage_id">
              <el-select v-model="form.stage_id" placeholder="选择阶段" style="width:100%">
                <el-option v-for="s in stages" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="赢单概率 (%)">
              <el-slider v-model="form.probability" :min="0" :max="100" show-input />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预计关闭日期">
              <el-date-picker v-model="form.close_date" type="date" placeholder="选择日期" style="width:100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="备注信息" />
        </el-form-item>

        <!-- ── Line Items (Products) ── -->
        <el-divider content-position="left">产品明细</el-divider>

        <div class="line-items-section">
          <el-table :data="lineItems" border size="small" style="width:100%" empty-text="暂未添加产品">
            <el-table-column label="产品" min-width="200">
              <template #default="{ row, $index }">
                <el-select
                  v-model="row.product_id"
                  placeholder="选择产品"
                  filterable
                  style="width:100%"
                  @change="onProductChange($index)"
                >
                  <el-option
                    v-for="p in products"
                    :key="p.id"
                    :label="`${p.name}${p.product_code ? ' (' + p.product_code + ')' : ''}`"
                    :value="p.id"
                  />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="数量" width="120">
              <template #default="{ row, $index }">
                <el-input-number
                  v-model="row.quantity"
                  :min="1"
                  size="small"
                  style="width:100%"
                  @change="recalcLineItem($index)"
                />
              </template>
            </el-table-column>
            <el-table-column label="单价 (元)" width="150">
              <template #default="{ row, $index }">
                <el-input-number
                  v-model="row.unit_price"
                  :min="0"
                  :precision="2"
                  size="small"
                  style="width:100%"
                  @change="recalcLineItem($index)"
                />
              </template>
            </el-table-column>
            <el-table-column label="小计 (元)" width="150">
              <template #default="{ row }">
                <span class="line-total">¥{{ (row.quantity * row.unit_price).toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80" align="center">
              <template #default="{ $index }">
                <el-button type="danger" link size="small" @click="removeLineItem($index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="line-items-actions">
            <el-button type="primary" size="small" @click="addLineItem">
              <el-icon style="margin-right:4px"><Plus /></el-icon>添加产品
            </el-button>
            <span class="line-items-total">合计: ¥{{ lineItemsTotal.toFixed(2) }}</span>
          </div>
        </div>

        <el-form-item style="margin-top:20px">
          <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { opportunitiesApi } from '../../api/opportunities'
import { accountsApi } from '../../api/accounts'
import { productsApi } from '../../api/products'
import type { Account, Stage, Product, LineItem } from '../../types/crm'

interface LineItemRow {
  _tempId: number
  product_id: number | undefined
  quantity: number
  unit_price: number
  id?: number  // server ID for existing items
  opportunity_id?: number
}

const route = useRoute()
const router = useRouter()
const formRef = ref()
const loading = ref(false)
const saving = ref(false)
const accounts = ref<Account[]>([])
const stages = ref<Stage[]>([])
const products = ref<Product[]>([])
const lineItems = ref<LineItemRow[]>([])

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  name: '',
  account_id: undefined as number | undefined,
  stage_id: undefined as number | undefined,
  amount: 0,
  probability: 0,
  close_date: undefined as string | undefined,
  description: '',
})

const rules = {
  name: [{ required: true, message: '请输入机会名称', trigger: 'blur' }],
  stage_id: [{ required: true, message: '请选择销售阶段', trigger: 'change' }],
}

const lineItemsTotal = computed(() =>
  lineItems.value.reduce((sum, row) => sum + (row.quantity || 0) * (row.unit_price || 0), 0)
)

let _nextTempId = 1

function addLineItem() {
  lineItems.value.push({
    _tempId: _nextTempId++,
    product_id: undefined,
    quantity: 1,
    unit_price: 0,
  })
}

function removeLineItem(index: number) {
  lineItems.value.splice(index, 1)
}

function onProductChange(index: number) {
  const row = lineItems.value[index]
  if (!row.product_id) return
  const product = products.value.find(p => p.id === row.product_id)
  if (product && product.price) {
    row.unit_price = product.price
  }
}

function recalcLineItem(_index: number) {
  // total is computed dynamically, no extra work needed
}

function goBack() {
  if (isEdit.value) {
    router.push(`/opportunities/${route.params.id}`)
  } else {
    router.push('/opportunities')
  }
}

onMounted(async () => {
  // Load accounts
  try {
    const { data } = await accountsApi.list({ page: 1, page_size: 100 })
    accounts.value = data.items
  } catch { /* ignore */ }

  // Load stages
  try {
    const { data } = await opportunitiesApi.getStages()
    stages.value = data
    if (!isEdit.value) {
      const defaultStage = data.find(s => !s.is_closed_won && !s.is_closed_lost)
      if (defaultStage) form.stage_id = defaultStage.id
    }
  } catch { /* ignore */ }

  // Load products
  try {
    const { data } = await productsApi.list({ page: 1, page_size: 100 })
    products.value = data.items
  } catch { /* ignore */ }

  // Load existing opportunity for edit
  if (isEdit.value) {
    loading.value = true
    try {
      const { data } = await opportunitiesApi.get(Number(route.params.id))
      Object.assign(form, data)

      // Load existing line items
      const liResp = await opportunitiesApi.listLineItems(Number(route.params.id))
      lineItems.value = liResp.data.map((li: LineItem) => ({
        _tempId: _nextTempId++,
        product_id: li.product_id,
        quantity: li.quantity,
        unit_price: li.unit_price,
        id: li.id,
        opportunity_id: li.opportunity_id,
      }))
    } catch {
      ElMessage.error('机会不存在')
      router.push('/opportunities')
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
      const oppId = Number(route.params.id)

      // Update opportunity fields
      await opportunitiesApi.update(oppId, form)

      // Sync line items: remove deleted ones, add new ones
      const existingIds = lineItems.value.filter(li => li.id).map(li => li.id!)
      // Get current server-side line items
      const liResp = await opportunitiesApi.listLineItems(oppId)
      const serverIds = liResp.data.map((li: LineItem) => li.id)

      // Delete items removed by user
      for (const sid of serverIds) {
        if (!existingIds.includes(sid)) {
          await opportunitiesApi.removeLineItem(oppId, sid).catch(() => {})
        }
      }

      // Add new items (no id yet) or update
      for (const row of lineItems.value) {
        if (!row.product_id) continue
        if (!row.id) {
          await opportunitiesApi.addLineItem(oppId, {
            product_id: row.product_id,
            quantity: row.quantity,
            unit_price: row.unit_price,
          })
        }
      }

      ElMessage.success('更新成功')
      router.push(`/opportunities/${oppId}`)
    } else {
      // Create opportunity first
      const { data: opp } = await opportunitiesApi.create(form as any)

      // Then add line items
      for (const row of lineItems.value) {
        if (!row.product_id) continue
        await opportunitiesApi.addLineItem(opp.id, {
          product_id: row.product_id,
          quantity: row.quantity,
          unit_price: row.unit_price,
        }).catch(() => {})
      }

      ElMessage.success('创建成功')
      router.push(`/opportunities/${opp.id}`)
    }
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.opportunity-form { max-width: 960px; }
.form-header {
  display: flex; align-items: center; gap: 12px; margin-bottom: 20px;
}
.page-title { margin: 0; font-size: 22px; color: #333; }

.line-items-section {
  margin-bottom: 16px;
}
.line-total {
  font-weight: 600;
  color: #1589ee;
}
.line-items-actions {
  display: flex; align-items: center; gap: 16px; margin-top: 12px;
}
.line-items-total {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-left: auto;
}
</style>
