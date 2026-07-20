<template>
  <div class="opportunity-detail" v-loading="loading">
    <div class="sf-page-header">
      <h2 class="sf-page-title">销售机会</h2>
    </div>

    <template v-if="opportunity">
      <RecordHeader
        :title="opportunity.name"
        icon-name="trend-chart"
        :hide-edit="!can('edit')"
        :hide-delete="!canDelete"
        @edit="$router.push(`/opportunities/${opportunity.id}/edit`)"
        @delete="handleDelete"
      />

      <!-- Salesforce-style Path component -->
      <div class="sf-path">
        <div class="sf-path-steps">
          <div
            v-for="(s, idx) in stages"
            :key="s.id"
            class="sf-path-step"
            :class="{
              active: opportunity.stage_id === s.id,
              complete: getStepIndex(s.id) < getStepIndex(opportunity.stage_id)
            }"
            @click="moveToStage(s.id)"
          >
            <div class="sf-path-step-label">{{ s.name }}</div>
            <div class="sf-path-step-date" v-if="opportunity.stage_id === s.id">
              {{ s.probability }}%
            </div>
          </div>
        </div>
      </div>

      <HighlightsPanel :items="highlightItems" />

      <RecordTabs :tabs="tabs">
        <template #panel-details>
          <RecordSection title="机会信息" :fields="oppFields" />
          <RecordSection title="系统信息" :fields="systemFields" />
        </template>
        <template #panel-products>
          <div class="sf-card">
            <div class="sf-card-header">
              <h3 class="sf-card-title">产品明细</h3>
            </div>
            <el-table :data="lineItems" border size="small" style="width:100%" empty-text="暂未关联产品">
              <el-table-column label="产品" min-width="200">
                <template #default="{ row }">
                  {{ productMap[row.product_id]?.name || `产品 #${row.product_id}` }}
                  <span v-if="productMap[row.product_id]?.product_code" class="product-code">
                    ({{ productMap[row.product_id]?.product_code }})
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="数量" width="100" align="center">
                <template #default="{ row }">{{ row.quantity }}</template>
              </el-table-column>
              <el-table-column label="单价" width="150" align="right">
                <template #default="{ row }">¥{{ row.unit_price.toFixed(2) }}</template>
              </el-table-column>
              <el-table-column label="小计" width="150" align="right">
                <template #default="{ row }">
                  <span class="line-total">¥{{ (row.quantity * row.unit_price).toFixed(2) }}</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </template>
        <template #panel-activity>
          <Timeline
            :entries="timelineEntries"
            :loading="timelineLoading"
            :has-more="timelineHasMore"
            @load-more="loadMoreTimeline"
          />
        </template>
      </RecordTabs>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { opportunitiesApi } from '../../api/opportunities'
import { productsApi } from '../../api/products'
import { auditLogsApi } from '../../api/auditLogs'
import { usePermissions } from '../../composables/usePermissions'
import type { Opportunity, Stage, LineItem, Product } from '../../types/crm'
import type { TimelineEntry } from '../../types/auditLog'
import RecordHeader from '../../components/record/RecordHeader.vue'
import RecordSection from '../../components/record/RecordSection.vue'
import HighlightsPanel from '../../components/record/HighlightsPanel.vue'
import RecordTabs from '../../components/record/RecordTabs.vue'
import Timeline from '../../components/activity/Timeline.vue'

const route = useRoute()
const router = useRouter()
const { can, canDelete } = usePermissions()
const opportunity = ref<Opportunity | null>(null)
const stages = ref<Stage[]>([])
const loading = ref(false)
const stageMap = ref<Record<string, Stage>>({})
const lineItems = ref<LineItem[]>([])
const productMap = ref<Record<string, Product>>({})

const timelineEntries = ref<TimelineEntry[]>([])
const timelineLoading = ref(false)
const timelinePage = ref(1)
const timelineHasMore = ref(true)

const tabs = computed(() => [
  { key: 'details', label: '详细信息' },
  { key: 'products', label: `产品明细${lineItems.value.length ? ` (${lineItems.value.length})` : ''}` },
  { key: 'activity', label: '活动' },
])

const highlightItems = computed(() => {
  const opp = opportunity.value
  if (!opp) return []
  const stage = stageMap.value[opp.stage_id]
  return [
    { label: '金额', apiName: 'amount', value: opp.amount || 0, type: 'currency' as const, flex: '1' },
    { label: '阶段', apiName: 'stage', value: stage?.name || '-', type: 'tag' as const,
      tagType: (stage?.is_closed_won ? 'success' : stage?.is_closed_lost ? 'danger' : 'primary') as any, flex: '1' },
    { label: '概率', apiName: 'probability', value: opp.probability || 0, type: 'percent' as const, flex: '1' },
    { label: '预计关闭日', apiName: 'close_date', value: opp.close_date || '-', flex: '1' },
  ]
})

const oppFields = computed(() => [
  { label: '金额', apiName: 'amount', value: opportunity.value?.amount ? `¥${opportunity.value.amount.toLocaleString()}` : '-' },
  { label: '销售阶段', apiName: 'stage', value: stageMap.value[opportunity.value?.stage_id || 0]?.name || '-' },
  { label: '赢单概率', apiName: 'probability', value: `${opportunity.value?.probability || 0}%` },
  { label: '预计关闭日', apiName: 'close_date', value: opportunity.value?.close_date || '-' },
  { label: '描述', apiName: 'description', value: opportunity.value?.description },
])

const systemFields = computed(() => [
  { label: '创建时间', apiName: 'created_at', value: opportunity.value?.created_at },
  { label: '更新时间', apiName: 'updated_at', value: opportunity.value?.updated_at },
])

function getStepIndex(stageId: string): number {
  return stages.value.findIndex(s => s.id === stageId)
}

async function moveToStage(stageId: string) {
  if (!opportunity.value || opportunity.value.stage_id === stageId) return
  try {
    await opportunitiesApi.update(opportunity.value.id, {
      stage_id: stageId,
      probability: stageMap.value[stageId]?.probability,
    })
    opportunity.value.stage_id = stageId
    opportunity.value.probability = stageMap.value[stageId]?.probability || 0
    ElMessage.success(`已移动到 "${stageMap.value[stageId]?.name}"`)
  } catch {
    ElMessage.error('移动失败')
  }
}

async function fetchOpportunity() {
  loading.value = true
  try {
    const { data } = await opportunitiesApi.get(route.params.id as string)
    opportunity.value = data
  } catch {
    ElMessage.error('机会不存在')
    router.push('/opportunities')
  } finally { loading.value = false }
}

async function fetchStages() {
  try {
    const { data } = await opportunitiesApi.getStages()
    stages.value = data
    data.forEach(s => { stageMap.value[s.id] = s })
  } catch { /* ignore */ }
}

async function handleDelete() {
  if (!opportunity.value) return
  try {
    await ElMessageBox.confirm(`确定删除机会 "${opportunity.value.name}" 吗？`, '确认删除', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
    await opportunitiesApi.delete(opportunity.value.id)
    ElMessage.success('删除成功')
    router.push('/opportunities')
  } catch { /* cancelled */ }
}

async function fetchLineItems() {
  if (!opportunity.value) return
  try {
    const { data: items } = await opportunitiesApi.listLineItems(opportunity.value.id)
    lineItems.value = items

    // Load product details for display
    const { data: prodData } = await productsApi.list({ page: 1, page_size: 100 })
    prodData.items.forEach(p => { productMap.value[p.id] = p })
  } catch { /* ignore */ }
}

async function loadTimeline() {
  if (!opportunity.value?.id) return
  timelineLoading.value = true
  try {
    const { data } = await auditLogsApi.getTimeline('opportunity', opportunity.value.id, timelinePage.value)
    if (timelinePage.value === 1) {
      timelineEntries.value = data
    } else {
      timelineEntries.value.push(...data)
    }
    timelineHasMore.value = data.length >= 20
  } catch {
    // silent
  } finally {
    timelineLoading.value = false
  }
}

function loadMoreTimeline() {
  timelinePage.value++
  loadTimeline()
}

watch(() => opportunity.value?.id, (id) => {
  if (id) {
    timelinePage.value = 1
    loadTimeline()
  }
})

onMounted(async () => {
  await fetchStages()
  await fetchOpportunity()
  if (opportunity.value) {
    await fetchLineItems()
  }
})
</script>

<style scoped>
.opportunity-detail { max-width: 960px; }

.sf-path {
  background: #ffffff;
  border: 1px solid #dddbda;
  border-radius: 3px;
  margin-bottom: 12px;
  overflow: hidden;
}

.sf-path-steps {
  display: flex;
}

.sf-path-step {
  flex: 1;
  text-align: center;
  padding: 10px 4px;
  cursor: pointer;
  transition: background 0.15s;
  border-right: 1px solid #dddbda;
}

.sf-path-step:last-child { border-right: none; }

.sf-path-step.active { background: #e8f0fe; }
.sf-path-step.active .sf-path-step-label { color: #1589ee; font-weight: 600; }
.sf-path-step.complete { background: #f4f6f9; }
.sf-path-step.complete .sf-path-step-label { color: #2e844a; }

.sf-path-step-label { font-size: 11px; color: #706e6b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sf-path-step-date { font-size: 10px; color: #c9c7c5; margin-top: 2px; }

.sf-card {
  background: #fff;
  border: 1px solid #dddbda;
  border-radius: 3px;
}
.sf-card-header {
  padding: 12px 16px;
  border-bottom: 1px solid #dddbda;
}
.sf-card-title { margin: 0; font-size: 14px; color: #333; }
.line-total { font-weight: 600; color: #1589ee; }
.product-code { color: #706e6b; font-size: 12px; }
</style>
