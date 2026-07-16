<template>
  <div class="territory-list">
    <div class="sf-page-header">
      <div class="sf-page-header-row">
        <h2 class="sf-page-title">销售区域</h2>
        <el-button type="primary" @click="showForm = true; editId = null">
          新建区域
        </el-button>
      </div>
    </div>

    <el-card shadow="hover">
      <el-tree
        :data="treeData"
        :props="treeProps"
        node-key="id"
        default-expand-all
        :expand-on-click-node="false"
        highlight-current
        @node-click="onNodeClick"
      >
        <template #default="{ node, data }">
          <div class="tree-node">
            <div class="tree-node-info">
              <span class="tree-node-name">{{ data.name }}</span>
              <span class="tree-node-code" v-if="data.code">({{ data.code }})</span>
              <span class="tree-node-type">{{ typeLabel(data.territory_type) }}</span>
            </div>
            <div class="tree-node-actions">
              <el-button link size="small" type="primary" @click.stop="editTerritory(data)">
                编辑
              </el-button>
              <el-button link size="small" type="danger" @click.stop="deleteTerritory(data)">
                删除
              </el-button>
            </div>
          </div>
        </template>
      </el-tree>
    </el-card>

    <!-- Territory Form Dialog -->
    <el-dialog
      v-model="showForm"
      :title="editId ? '编辑区域' : '新建区域'"
      width="600px"
      destroy-on-close
    >
      <TerritoryForm
        :territory-id="editId"
        @saved="onSaved"
        @cancel="showForm = false"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { territoriesApi } from '../../api/territories'
import type { TerritoryTreeNode } from '../../types/territory'
import TerritoryForm from './TerritoryForm.vue'

const router = useRouter()

const treeData = ref<TerritoryTreeNode[]>([])
const treeProps = { children: 'children', label: 'name' }
const showForm = ref(false)
const editId = ref<number | null>(null)

function typeLabel(type: string): string {
  const map: Record<string, string> = { region: '大区', district: '区域', branch: '分部', custom: '自定义' }
  return map[type] || type
}

async function fetchTree() {
  try {
    const { data } = await territoriesApi.getTree()
    treeData.value = data
  } catch { /* ignore */ }
}

function onNodeClick(data: TerritoryTreeNode) {
  router.push(`/admin/territories/${data.id}`)
}

function editTerritory(data: TerritoryTreeNode) {
  editId.value = data.id
  showForm.value = true
}

async function deleteTerritory(data: TerritoryTreeNode) {
  try {
    await ElMessageBox.confirm(`确定删除区域 "${data.name}" 吗？`, '确认删除', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
    await territoriesApi.delete(data.id)
    ElMessage.success('删除成功')
    await fetchTree()
  } catch { /* cancelled */ }
}

function onSaved() {
  showForm.value = false
  editId.value = null
  fetchTree()
}

onMounted(fetchTree)
</script>

<style scoped>
.sf-page-header-row {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;
}
.sf-page-title { margin: 0; font-size: 22px; color: #333; }

.tree-node {
  display: flex; align-items: center; justify-content: space-between;
  padding: 4px 0; width: 100%;
}
.tree-node-info { display: flex; align-items: center; gap: 8px; }
.tree-node-name { font-weight: 500; font-size: 14px; }
.tree-node-code { color: #706e6b; font-size: 12px; }
.tree-node-type {
  font-size: 11px; color: #fff; background: #1589ee; border-radius: 3px;
  padding: 1px 6px;
}
.tree-node-actions { opacity: 0; transition: opacity 0.15s; }
.tree-node:hover .tree-node-actions { opacity: 1; }
</style>
