<template>
  <div class="pipeline-board">
    <div class="sf-page-header">
      <h2 class="sf-page-title">管道看板</h2>
      <div class="sf-page-actions">
        <router-link to="/opportunities/new">
          <el-button type="primary" size="small" icon="plus">新建机会</el-button>
        </router-link>
        <router-link to="/opportunities">
          <el-button size="small" icon="list">列表视图</el-button>
        </router-link>
      </div>
    </div>

    <!-- Summary cards -->
    <el-row :gutter="12" class="summary-row">
      <el-col :span="6" v-for="card in summaryCards" :key="card.label">
        <div class="sf-card">
          <div class="sf-card-body" style="display:flex;align-items:center;gap:12px;padding:10px 14px;">
            <div style="flex:1">
              <div class="summary-value" :style="{ color: card.color }">{{ card.value }}</div>
              <div class="summary-label">{{ card.label }}</div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Kanban columns -->
    <div class="kanban-container" v-loading="loading">
      <div
        class="kanban-column"
        v-for="stageData in pipeline.stages"
        :key="stageData.stage.id"
        @dragover.prevent="onDragOver($event, stageData.stage.id)"
        @drop.prevent="onDrop($event, stageData.stage.id)"
        @dragleave="onDragLeave"
      >
        <div class="kanban-column-header" :class="getStageClass(stageData.stage)">
          <div class="kanban-column-title">
            <span>{{ stageData.stage.name }}</span>
            <span class="kanban-badge">{{ stageData.count }}</span>
          </div>
          <div class="kanban-column-amount">¥{{ (stageData.total_amount || 0).toLocaleString() }}</div>
        </div>

        <div class="kanban-cards" ref="columnRefs">
          <div
            v-for="opp in stageData.opportunities"
            :key="opp.id"
            class="kanban-card"
            draggable="true"
            @dragstart="onDragStart($event, opp)"
            @dragend="onDragEnd"
            @click="$router.push(`/opportunities/${opp.id}`)"
          >
            <div class="kanban-card-title">{{ opp.name }}</div>
            <div class="kanban-card-meta">
              <span class="kanban-card-amount">¥{{ (opp.amount || 0).toLocaleString() }}</span>
              <span class="kanban-card-prob">{{ opp.probability || 0 }}%</span>
            </div>
            <div class="kanban-card-footer" v-if="opp.close_date">
              <el-icon size="12"><calendar /></el-icon>
              <span>{{ opp.close_date }}</span>
            </div>
          </div>

          <div v-if="stageData.opportunities.length === 0" class="kanban-empty">
            没有机会
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { opportunitiesApi } from '../../api/opportunities'
import type { PipelineData, Opportunity, Stage } from '../../types/crm'
import { Calendar } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const pipeline = reactive<PipelineData>({ stages: [] })
const draggingOpp = ref<Opportunity | null>(null)

const summaryCards = computed(() => {
  const totalAmount = pipeline.stages.reduce((s, st) => s + (st.total_amount || 0), 0)
  const totalCount = pipeline.stages.reduce((s, st) => s + st.count, 0)
  const won = pipeline.stages.find(s => s.stage.is_closed_won)
  const wonAmount = won?.total_amount || 0
  const avgAmount = totalCount ? Math.round(totalAmount / totalCount) : 0
  return [
    { label: '管道总额', value: `¥${totalAmount.toLocaleString()}`, color: '#1589ee' },
    { label: '机会总数', value: String(totalCount), color: '#2e844a' },
    { label: '赢单金额', value: `¥${wonAmount.toLocaleString()}`, color: '#2e844a' },
    { label: '平均金额', value: `¥${avgAmount.toLocaleString()}`, color: '#dd7a01' },
  ]
})

function getStageClass(stage: Stage) {
  if (stage.is_closed_won) return 'stage-won'
  if (stage.is_closed_lost) return 'stage-lost'
  if (stage.probability >= 70) return 'stage-hot'
  return ''
}

function onDragStart(e: DragEvent, opp: Opportunity) {
  draggingOpp.value = opp
  if (e.dataTransfer) {
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', String(opp.id))
  }
  setTimeout(() => (e.target as HTMLElement)?.classList.add('dragging'), 0)
}

function onDragEnd(e: DragEvent) {
  (e.target as HTMLElement)?.classList.remove('dragging')
  draggingOpp.value = null
  document.querySelectorAll('.kanban-column').forEach(el => el.classList.remove('drag-over'))
}

function onDragOver(e: DragEvent, _stageId: string) {
  if (e.dataTransfer) e.dataTransfer.dropEffect = 'move'
  ;(e.currentTarget as HTMLElement).classList.add('drag-over')
}

function onDragLeave(e: DragEvent) {
  ;(e.currentTarget as HTMLElement).classList.remove('drag-over')
}

async function onDrop(e: DragEvent, targetStageId: string) {
  ;(e.currentTarget as HTMLElement).classList.remove('drag-over')
  const opp = draggingOpp.value
  if (!opp || opp.stage_id === targetStageId) return

  const source = pipeline.stages.find(s => s.stage.id === opp.stage_id)
  const target = pipeline.stages.find(s => s.stage.id === targetStageId)
  if (!source || !target) return

  const idx = source.opportunities.findIndex(o => o.id === opp.id)
  if (idx === -1) return

  source.opportunities.splice(idx, 1)
  source.count--
  source.total_amount -= (opp.amount || 0)

  const updated = { ...opp, stage_id: targetStageId }
  target.opportunities.push(updated)
  target.count++
  target.total_amount += (opp.amount || 0)

  try {
    await opportunitiesApi.update(opp.id, {
      stage_id: targetStageId,
      probability: target.stage.probability,
    })
    ElMessage.success(`已移到 "${target.stage.name}"`)
  } catch {
    ElMessage.error('移动失败，已回滚')
    fetchPipeline()
  }
}

async function fetchPipeline() {
  loading.value = true
  try {
    const { data } = await opportunitiesApi.getPipeline()
    pipeline.stages = data.stages
  } catch {
    ElMessage.error('获取管道数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchPipeline)
</script>

<style scoped>
.pipeline-board { display: flex; flex-direction: column; height: calc(100vh - 100px); }

.summary-row { margin-bottom: 12px; }

.summary-icon {
  width: 40px; height: 40px; border-radius: 4px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.summary-value { font-size: 18px; font-weight: 700; line-height: 1.2; }
.summary-label { font-size: 11px; color: #706e6b; margin-top: 2px; }

.kanban-container {
  display: flex; gap: 12px; flex: 1; overflow-x: auto; padding-bottom: 8px;
}

.kanban-column {
  min-width: 240px; max-width: 280px; flex: 1;
  background: #f0f2f5; border-radius: 4px;
  display: flex; flex-direction: column;
  transition: background 0.2s;
}

.kanban-column.drag-over { background: #e6f7ff; outline: 2px dashed #409eff; }

.kanban-column-header {
  padding: 10px 12px; border-radius: 4px 4px 0 0;
  background: #fff; border-bottom: 3px solid #1589ee;
}

.kanban-column-header.stage-won { border-bottom-color: #2e844a; }
.kanban-column-header.stage-lost { border-bottom-color: #c23934; }
.kanban-column-header.stage-hot { border-bottom-color: #dd7a01; }

.kanban-column-title {
  display: flex; justify-content: space-between; align-items: center;
  font-weight: 600; font-size: 13px; color: #080707;
}

.kanban-badge {
  font-size: 10px; background: #dddbda; color: #514f4d;
  padding: 1px 6px; border-radius: 10px; font-weight: 400;
}

.kanban-column-amount { font-size: 11px; color: #706e6b; margin-top: 2px; }

.kanban-cards {
  flex: 1; overflow-y: auto; padding: 6px;
  display: flex; flex-direction: column; gap: 6px;
}

.kanban-card {
  background: #fff; border-radius: 4px; padding: 10px 12px;
  cursor: grab; border: 1px solid #e5e4e2;
  transition: box-shadow 0.15s, transform 0.1s;
  user-select: none;
}

.kanban-card:hover {
  box-shadow: 0 1px 4px rgba(0,0,0,0.1); transform: translateY(-1px);
}

.kanban-card.dragging { opacity: 0.4; transform: rotate(3deg); }

.kanban-card-title { font-weight: 600; font-size: 13px; color: #080707; margin-bottom: 6px; }

.kanban-card-meta {
  display: flex; justify-content: space-between; font-size: 12px;
}

.kanban-card-amount { color: #1589ee; font-weight: 600; }
.kanban-card-prob { color: #dd7a01; }

.kanban-card-footer {
  display: flex; align-items: center; gap: 4px;
  margin-top: 6px; font-size: 11px; color: #999;
}

.kanban-empty {
  color: #bbb; font-size: 12px; text-align: center; padding: 20px 0;
}
</style>
