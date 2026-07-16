<template>
  <div class="sf-related-list">
    <div class="sf-related-list-header">
      <div class="sf-related-list-left">
        <span class="sf-related-list-title">{{ title }}</span>
        <span v-if="total !== undefined" class="sf-related-list-count">({{ total }})</span>
      </div>
      <div class="sf-related-list-actions">
        <slot name="actions">
          <el-button v-if="createRoute" size="small" type="primary" plain icon="plus" @click="$router.push(createRoute)">
            {{ createLabel || '新建' }}
          </el-button>
        </slot>
      </div>
    </div>

    <div class="sf-related-list-body">
      <el-table
        :data="items"
        class="sf-table-compact"
        size="small"
        stripe
        style="width: 100%"
        v-loading="loading"
        @row-click="rowClick && $router.push(rowClick(row))"
      >
        <el-table-column
          v-for="col in columns"
          :key="col.prop"
          :prop="col.prop"
          :label="col.label"
          :width="col.width"
          :min-width="col.minWidth"
          :formatter="col.formatter"
        >
          <template v-if="col.slot" #default="{ row }">
            <slot :name="'col-' + col.prop" :row="row" :value="row[col.prop]">
              <span>{{ row[col.prop] }}</span>
            </slot>
          </template>
        </el-table-column>
        <el-table-column v-if="actions" label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <slot name="row-actions" :row="row">
              <el-button size="small" text type="primary" @click.stop="actions.view && $router.push(actions.view(row))">
                查看
              </el-button>
            </slot>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
export interface RelatedColumn {
  prop: string
  label: string
  width?: number
  minWidth?: number
  formatter?: (row: any, column: any, cellValue: any, index: number) => string
  slot?: boolean
}

defineProps<{
  title: string
  total?: number
  items: any[]
  columns: RelatedColumn[]
  loading?: boolean
  createRoute?: string
  createLabel?: string
  actions?: {
    view: (row: any) => string
  }
  rowClick?: (row: any) => string
}>()
</script>

<style scoped>
.sf-related-list {
  background: #ffffff;
  border: 1px solid #dddbda;
  border-radius: 3px;
  margin-bottom: 12px;
}

.sf-related-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 14px;
  border-bottom: 1px solid #dddbda;
  background: #fafafa;
}

.sf-related-list-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.sf-related-list-title {
  font-size: 12px;
  font-weight: 700;
  color: #514f4d;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.sf-related-list-count {
  font-size: 11px;
  color: #706e6b;
}

.sf-related-list-body {
  overflow-x: auto;
}

:deep(.el-table__header th) {
  background: #fafafa !important;
  font-size: 11px !important;
  color: #514f4d !important;
  font-weight: 600 !important;
  padding: 4px 8px !important;
}
</style>
