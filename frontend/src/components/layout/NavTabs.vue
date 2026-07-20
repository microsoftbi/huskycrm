<template>
  <div class="sf-nav-tabs">
    <div class="sf-nav-tabs-inner">
      <router-link
        v-for="tab in tabs"
        :key="tab.path"
        :to="tab.path"
        class="sf-nav-tab"
        :class="{ active: isActive(tab.path) }"
      >
        <el-icon :size="16" class="sf-nav-tab-icon">
          <component :is="tab.icon" />
        </el-icon>
        <span class="sf-nav-tab-label">{{ tab.label }}</span>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()

const tabs = [
  { path: '/', label: '仪表盘', icon: 'odometer' },
  { path: '/accounts', label: '账户', icon: 'office-building' },
  { path: '/contacts', label: '联系人', icon: 'user' },
  { path: '/products', label: '产品', icon: 'box' },
  { path: '/events', label: '拜访', icon: 'phone' },
  { path: '/opportunities', label: '销售机会', icon: 'TrendCharts' },
  { path: '/leads', label: '线索', icon: 'aim' },
  { path: '/campaigns', label: '活动', icon: 'collection-tag' },
  { path: '/admin/approval-queue', label: '审批', icon: 'finished' },
  { path: '/admin/recycle-bin', label: '回收站', icon: 'delete' },
]

function isActive(path: string): boolean {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<style scoped>
.sf-nav-tabs {
  background: #ffffff;
  border-bottom: 1px solid #dddbda;
  padding: 0 12px;
  overflow: hidden;
}

.sf-nav-tabs-inner {
  display: flex;
  gap: 2px;
  overflow-x: auto;
  scrollbar-width: none;
}

.sf-nav-tabs-inner::-webkit-scrollbar {
  display: none;
}

.sf-nav-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  font-size: 12px;
  font-weight: 500;
  color: #514f4d;
  text-decoration: none;
  white-space: nowrap;
  border-bottom: 3px solid transparent;
  transition: color 0.12s, border-color 0.12s, background 0.12s;
  cursor: pointer;
  user-select: none;
}

.sf-nav-tab:hover {
  color: #1589ee;
  background: #f4f6f9;
}

.sf-nav-tab.active {
  color: #1589ee;
  border-bottom-color: #1589ee;
  font-weight: 600;
  background: #ffffff;
}

.sf-nav-tab-icon {
  flex-shrink: 0;
}
</style>
