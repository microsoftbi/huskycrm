<template>
  <div class="sf-highlights">
    <div class="sf-highlights-inner">
      <div v-for="(item, index) in items" :key="index" class="sf-highlight-item" :style="{ flex: item.flex || '1' }">
        <div class="sf-highlight-label">{{ item.label }}</div>
        <div class="sf-highlight-value" :class="{ 'is-link': item.link }" @click="item.link && $router.push(item.link)">
          <slot :name="item.apiName" :value="item.value">
            <template v-if="item.type === 'currency'">
              ¥{{ formatNumber(item.value) }}
            </template>
            <template v-else-if="item.type === 'percent'">
              {{ item.value || 0 }}%
            </template>
            <template v-else-if="item.type === 'tag'">
              <el-tag :type="item.tagType || 'info'" size="small">{{ item.value || '-' }}</el-tag>
            </template>
            <template v-else>
              {{ item.value || '-' }}
            </template>
          </slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
export interface HighlightItem {
  label: string
  apiName: string
  value: any
  type?: 'text' | 'currency' | 'percent' | 'tag'
  tagType?: 'success' | 'warning' | 'danger' | 'info' | 'primary'
  link?: string
  flex?: string
}

defineProps<{
  items: HighlightItem[]
}>()

function formatNumber(val: number | null | undefined): string {
  if (val == null) return '0'
  return Number(val).toLocaleString()
}
</script>

<style scoped>
.sf-highlights {
  background: #ffffff;
  border: 1px solid #dddbda;
  border-radius: 3px;
  margin-bottom: 12px;
  overflow: hidden;
}

.sf-highlights-inner {
  display: flex;
  flex-wrap: wrap;
}

.sf-highlight-item {
  padding: 10px 14px;
  min-width: 120px;
  border-right: 1px solid #f3f2f2;
  border-bottom: 1px solid #f3f2f2;
}

.sf-highlight-item:last-child {
  border-right: none;
}

.sf-highlight-label {
  font-size: 10px;
  color: #706e6b;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  margin-bottom: 4px;
  font-weight: 600;
}

.sf-highlight-value {
  font-size: 14px;
  color: #080707;
  font-weight: 600;
}

.sf-highlight-value.is-link {
  color: #1589ee;
  cursor: pointer;
}

.sf-highlight-value.is-link:hover {
  text-decoration: underline;
}
</style>
