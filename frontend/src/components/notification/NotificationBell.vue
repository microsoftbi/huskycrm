<template>
  <el-popover
    placement="bottom-end"
    :width="360"
    trigger="click"
    :popper-style="{ padding: '0' }"
    @show="handleShow"
  >
    <template #reference>
      <el-badge :value="unreadCount" :hidden="unreadCount === 0" :max="99" class="notif-badge">
        <el-button size="small" circle class="notif-button">
          <el-icon :size="18"><bell /></el-icon>
        </el-button>
      </el-badge>
    </template>
    <NotificationDropdown />
  </el-popover>
</template>

<script setup lang="ts">
import { Bell } from '@element-plus/icons-vue'
import { useNotifications } from '../../composables/useNotifications'
import NotificationDropdown from './NotificationDropdown.vue'

const { unreadCount, fetchRecent } = useNotifications()

function handleShow() {
  fetchRecent()
}
</script>

<style scoped>
.notif-badge { line-height: 1; }
.notif-button { border: none; background: transparent; }
.notif-button:hover { background: #f4f6f9; }
</style>