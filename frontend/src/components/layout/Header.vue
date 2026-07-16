<template>
  <header class="sf-header">
    <!-- Left: App Launcher + Logo -->
    <div class="sf-header-left">
      <div class="sf-app-launcher" @click="handleAppLauncher">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#706e6b" stroke-width="2" stroke-linecap="round">
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
      <span class="sf-logo">Husky CRM</span>
    </div>

    <!-- Center: Global Search -->
    <div class="sf-header-center">
      <div class="sf-global-search">
        <el-input
          v-model="searchQuery"
          placeholder="搜索记录..."
          size="small"
          clearable
          :prefix-icon="SearchIcon"
          @keyup.enter="handleSearch"
        />
      </div>
    </div>

    <!-- Right: Actions + User -->
    <div class="sf-header-right">
      <el-dropdown trigger="click" @command="handleQuickCreate">
        <el-button type="primary" size="small" icon="plus">新建</el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="account"><el-icon><office-building /></el-icon>账户</el-dropdown-item>
            <el-dropdown-item command="contact"><el-icon><user /></el-icon>联系人</el-dropdown-item>
            <el-dropdown-item command="opportunity"><el-icon><trend-chart /></el-icon>销售机会</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>

      <el-button size="small" circle :icon="Setting">
        <el-icon><setting /></el-icon>
      </el-button>

      <el-dropdown trigger="click" @command="handleCommand">
        <div class="sf-user-info">
          <div class="sf-user-avatar">{{ userInitial }}</div>
          <span class="sf-user-name">{{ auth.user?.display_name || auth.user?.username }}</span>
          <el-icon size="10"><arrow-down /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile"><el-icon><user /></el-icon>个人信息</el-dropdown-item>
            <el-dropdown-item divided command="logout"><el-icon><switch-button /></el-icon>退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Search as SearchIcon, Setting } from '@element-plus/icons-vue'
import { useAuthStore } from '../../stores/authStore'

const router = useRouter()
const auth = useAuthStore()
const searchQuery = ref('')

const userInitial = computed(() => {
  const name = auth.user?.display_name || auth.user?.username || 'U'
  return name[0].toUpperCase()
})

function handleSearch() {
  if (!searchQuery.value.trim()) return
  router.push(`/accounts?search=${encodeURIComponent(searchQuery.value)}`)
}

function handleQuickCreate(cmd: string) {
  const routes: Record<string, string> = {
    account: '/accounts/new',
    contact: '/contacts/new',
    opportunity: '/opportunities/new',
  }
  if (routes[cmd]) router.push(routes[cmd])
}

function handleCommand(command: string) {
  if (command === 'logout') {
    auth.logout()
    router.push('/login')
  }
}

function handleAppLauncher() {
  // App launcher - could show app switching menu
}
</script>

<style scoped>
.sf-header {
  display: flex;
  align-items: center;
  height: 48px;
  padding: 0 14px;
  background: #ffffff;
  border-bottom: 1px solid #dddbda;
  gap: 12px;
}

.sf-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.sf-app-launcher {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.1s;
}

.sf-app-launcher:hover {
  background: #f4f6f9;
}

.sf-logo {
  font-size: 16px;
  font-weight: 700;
  color: #080707;
  letter-spacing: -0.2px;
}

.sf-header-center {
  flex: 1;
  display: flex;
  justify-content: center;
  max-width: 480px;
  margin: 0 auto;
}

.sf-global-search {
  width: 100%;
}

.sf-global-search :deep(.el-input__wrapper) {
  background: #f4f6f9;
  border-radius: 4px;
  border: 1px solid transparent;
}

.sf-global-search :deep(.el-input__wrapper.is-focus) {
  background: #fff;
  border-color: #1589ee;
}

.sf-header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.sf-user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 3px;
  transition: background 0.1s;
}

.sf-user-info:hover {
  background: #f4f6f9;
}

.sf-user-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: #1589ee;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
}

.sf-user-name {
  font-size: 12px;
  color: #3e3e3c;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
