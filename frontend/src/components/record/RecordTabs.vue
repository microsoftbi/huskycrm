<template>
  <div class="sf-tabs-wrapper">
    <div class="sf-tabs-header">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="sf-tab-btn"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
        <span v-if="tab.count !== undefined" class="sf-tab-count">{{ tab.count }}</span>
      </button>
    </div>
    <div class="sf-tab-content">
      <slot :name="activeTab">
        <div v-for="tab in tabs" :key="tab.key" v-show="activeTab === tab.key">
          <slot :name="'panel-' + tab.key" />
        </div>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

export interface TabItem {
  key: string
  label: string
  count?: number
}

const props = defineProps<{
  tabs: TabItem[]
  defaultTab?: string
}>()

const activeTab = ref(props.defaultTab || (props.tabs[0]?.key ?? ''))
</script>

<style scoped>
.sf-tabs-wrapper {
  background: #ffffff;
  border: 1px solid #dddbda;
  border-radius: 3px;
  margin-bottom: 12px;
  overflow: hidden;
}

.sf-tabs-header {
  display: flex;
  border-bottom: 1px solid #dddbda;
  background: #fafafa;
  overflow-x: auto;
}

.sf-tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  font-size: 12px;
  font-weight: 600;
  color: #514f4d;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  white-space: nowrap;
  transition: color 0.1s, border-color 0.1s, background 0.1s;
}

.sf-tab-btn:hover {
  background: #f4f6f9;
  color: #1589ee;
}

.sf-tab-btn.active {
  color: #1589ee;
  border-bottom-color: #1589ee;
  background: #ffffff;
}

.sf-tab-count {
  font-size: 10px;
  background: #dddbda;
  color: #514f4d;
  padding: 1px 6px;
  border-radius: 10px;
  font-weight: 400;
}

.sf-tab-content {
  padding: 0;
}
</style>
