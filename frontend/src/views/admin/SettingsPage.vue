<template>
  <div class="settings-page">
    <!-- Left: Menu -->
    <div class="settings-sidebar">
      <div class="settings-menu-header">
        <h3 class="settings-menu-title">设置</h3>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="settings-menu"
        @select="onMenuSelect"
      >
        <el-menu-item index="users">
          <el-icon><user /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="territories">
          <el-icon><map-location /></el-icon>
          <span>区域管理</span>
        </el-menu-item>
        <el-menu-item index="profiles">
          <el-icon><setting /></el-icon>
          <span>Profile管理</span>
        </el-menu-item>
        <el-menu-item index="validation-rules">
          <el-icon><checked /></el-icon>
          <span>验证规则</span>
        </el-menu-item>
        <el-menu-item index="duplicate-rules">
          <el-icon><copy-document /></el-icon>
          <span>重复检测</span>
        </el-menu-item>
        <el-menu-item index="approval-rules">
          <el-icon><finished /></el-icon>
          <span>审批规则</span>
        </el-menu-item>
        <el-menu-item index="lead-assignment-rules">
          <el-icon><share /></el-icon>
          <span>线索分配规则</span>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- Right: Content -->
    <div class="settings-content">
      <UserManagement v-if="activeMenu === 'users'" />
      <TerritoryList v-if="activeMenu === 'territories'" />
      <ProfileManagement v-if="activeMenu === 'profiles'" />
      <ValidationRuleManagement v-if="activeMenu === 'validation-rules'" />
      <DuplicateRuleManagement v-if="activeMenu === 'duplicate-rules'" />
      <ApprovalRuleManagement v-if="activeMenu === 'approval-rules'" />
      <LeadAssignmentRuleManagement v-if="activeMenu === 'lead-assignment-rules'" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Checked } from '@element-plus/icons-vue'
import UserManagement from './UserManagement.vue'
import TerritoryList from '../territories/TerritoryList.vue'
import ProfileManagement from './ProfileManagement.vue'
import ValidationRuleManagement from './ValidationRuleManagement.vue'
import DuplicateRuleManagement from './DuplicateRuleManagement.vue'
import ApprovalRuleManagement from './ApprovalRuleManagement.vue'
import LeadAssignmentRuleManagement from './LeadAssignmentRuleManagement.vue'

const route = useRoute()
const router = useRouter()

const activeMenu = ref<string>((route.query?.section as string) || 'users')

function onMenuSelect(index: string) {
  activeMenu.value = index
  router.replace({ query: { section: index } })
}
</script>

<style scoped>
.settings-page {
  display: flex;
  height: 100%;
  gap: 0;
  background: #fff;
  border: 1px solid #dddbda;
  border-radius: 3px;
  overflow: hidden;
}

.settings-sidebar {
  width: 220px;
  min-width: 220px;
  border-right: 1px solid #dddbda;
  background: #f8f8f8;
  display: flex;
  flex-direction: column;
}

.settings-menu-header {
  padding: 14px 16px;
  border-bottom: 1px solid #dddbda;
}

.settings-menu-title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #080707;
}

.settings-menu {
  border-right: none;
  background: transparent;
}

.settings-menu :deep(.el-menu-item) {
  height: 40px;
  line-height: 40px;
  font-size: 13px;
  color: #3e3e3c;
  border-left: 3px solid transparent;
}

.settings-menu :deep(.el-menu-item.is-active) {
  background: #e8f0fe;
  border-left-color: #1589ee;
  color: #1589ee;
  font-weight: 600;
}

.settings-menu :deep(.el-menu-item:hover) {
  background: #f4f6f9;
}

.settings-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #fff;
}
</style>