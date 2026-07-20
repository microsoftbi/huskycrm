<template>
  <aside class="sf-sidebar">
    <!-- App Launcher + Logo -->
    <div class="sf-sidebar-header">
      <el-dropdown trigger="click" @command="handleAppCommand">
        <div class="sf-app-launcher">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#706e6b" stroke-width="2">
            <rect x="3" y="3" width="4" height="4" rx="1"/>
            <rect x="10" y="3" width="4" height="4" rx="1"/>
            <rect x="17" y="3" width="4" height="4" rx="1"/>
            <rect x="3" y="10" width="4" height="4" rx="1"/>
            <rect x="10" y="10" width="4" height="4" rx="1"/>
            <rect x="17" y="10" width="4" height="4" rx="1"/>
            <rect x="3" y="17" width="4" height="4" rx="1"/>
            <rect x="10" y="17" width="4" height="4" rx="1"/>
            <rect x="17" y="17" width="4" height="4" rx="1"/>
          </svg>
        </div>
      </el-dropdown>
      <span class="sf-sidebar-logo">Husky CRM</span>
    </div>

    <!-- Navigation -->
    <nav class="sf-sidebar-nav">
      <div class="sf-nav-section-title">核心</div>

      <router-link to="/" class="sf-nav-item" :class="{ active: route.path === '/' }">
        <span class="sf-nav-icon"><el-icon :size="16"><odometer /></el-icon></span>
        <span>仪表盘</span>
      </router-link>

      <div class="sf-nav-section-title">CRM</div>

      <router-link to="/accounts" class="sf-nav-item" :class="{ active: route.path.startsWith('/accounts') }">
        <span class="sf-nav-icon"><el-icon :size="16"><office-building /></el-icon></span>
        <span>账户</span>
      </router-link>

      <router-link to="/contacts" class="sf-nav-item" :class="{ active: route.path.startsWith('/contacts') }">
        <span class="sf-nav-icon"><el-icon :size="16"><user /></el-icon></span>
        <span>联系人</span>
      </router-link>

      <router-link to="/opportunities" class="sf-nav-item" :class="{ active: route.path.startsWith('/opportunities') }">
        <span class="sf-nav-icon"><el-icon :size="16"><trend-charts /></el-icon></span>
        <span>销售机会</span>
      </router-link>

      <div class="sf-nav-section-title">管理</div>

      <router-link v-if="isAdmin" to="/admin/objects" class="sf-nav-item" :class="{ active: route.path.startsWith('/admin/objects') }">
        <span class="sf-nav-icon"><el-icon :size="16"><grid /></el-icon></span>
        <span>自定义对象</span>
      </router-link>

      <router-link v-if="isAdmin" to="/admin/workflows" class="sf-nav-item" :class="{ active: route.path.startsWith('/admin/workflows') }">
        <span class="sf-nav-icon"><el-icon :size="16"><set-up /></el-icon></span>
        <span>工作流</span>
      </router-link>

      <router-link to="/admin/reports" class="sf-nav-item" :class="{ active: route.path.startsWith('/admin/reports') }">
        <span class="sf-nav-icon"><el-icon :size="16"><data-analysis /></el-icon></span>
        <span>报表</span>
      </router-link>

      <router-link to="/admin/dashboards" class="sf-nav-item" :class="{ active: route.path.startsWith('/admin/dashboards') }">
        <span class="sf-nav-icon"><el-icon :size="16"><data-board /></el-icon></span>
        <span>仪表盘</span>
      </router-link>
    </nav>

    <!-- User profile at bottom -->
    <div class="sf-sidebar-footer">
      <div class="sf-sidebar-user" @click="handleUserClick">
        <div class="sf-sidebar-avatar">{{ userInitial }}</div>
        <div class="sf-sidebar-user-info">
          <div class="sf-sidebar-user-name">{{ auth.user?.display_name || auth.user?.username || 'User' }}</div>
          <div class="sf-sidebar-user-email">{{ auth.user?.email || '' }}</div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/authStore'
import { usePermissions } from '../../composables/usePermissions'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const { isAdmin } = usePermissions()

const userInitial = computed(() => {
  const name = auth.user?.display_name || auth.user?.username || 'U'
  return name[0].toUpperCase()
})

function handleAppCommand(cmd: string) {
  if (cmd === 'logout') {
    auth.logout()
    router.push('/login')
  }
}

function handleUserClick() {
  // Could open user profile dropdown
}
</script>

<style scoped>
.sf-sidebar {
  width: 240px;
  min-width: 240px;
  background: #ffffff;
  border-right: 1px solid #dddbda;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.sf-sidebar-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-bottom: 1px solid #dddbda;
  min-height: 50px;
}

.sf-app-launcher {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  cursor: pointer;
  border-radius: 3px;
  transition: background 0.1s;
}

.sf-app-launcher:hover {
  background: #f4f6f9;
}

.sf-sidebar-logo {
  font-size: 17px;
  font-weight: 700;
  color: #080707;
  letter-spacing: -0.3px;
}

.sf-sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 4px 0;
}

.sf-nav-section-title {
  font-size: 10px;
  font-weight: 700;
  color: #514f4d;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  padding: 12px 14px 4px;
}

.sf-nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 14px;
  color: #3e3e3c;
  font-size: 13px;
  cursor: pointer;
  text-decoration: none;
  border-left: 3px solid transparent;
  transition: background 0.1s, border-color 0.1s;
  margin: 1px 0;
}

.sf-nav-item:hover {
  background: #f4f6f9;
  color: #080707;
}

.sf-nav-item.active {
  background: #e8f0fe;
  border-left-color: #1589ee;
  color: #1589ee;
  font-weight: 600;
}

.sf-nav-icon {
  width: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #706e6b;
  flex-shrink: 0;
}

.sf-nav-item.active .sf-nav-icon {
  color: #1589ee;
}

.sf-sidebar-footer {
  border-top: 1px solid #dddbda;
  padding: 8px 10px;
}

.sf-sidebar-user {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 4px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.1s;
}

.sf-sidebar-user:hover {
  background: #f4f6f9;
}

.sf-sidebar-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #1589ee;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}

.sf-sidebar-user-name {
  font-size: 12px;
  font-weight: 600;
  color: #080707;
  line-height: 1.2;
}

.sf-sidebar-user-email {
  font-size: 10px;
  color: #706e6b;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
