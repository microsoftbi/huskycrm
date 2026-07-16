<template>
  <div class="sf-record-header">
    <div class="sf-record-icon">
      <el-icon :size="20"><component :is="iconName" /></el-icon>
    </div>
    <div class="sf-record-name">{{ title }}</div>
    <div class="sf-record-actions">
      <el-button v-if="!hideEdit" type="primary" size="small" icon="edit" @click="$emit('edit')">编辑</el-button>
      <el-button v-if="!hideDelete" size="small" type="danger" plain icon="delete" @click="$emit('delete')">删除</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  iconName?: string
  hideEdit?: boolean
  hideDelete?: boolean
}>()

defineEmits<{
  edit: []
  delete: []
}>()
</script>

<style scoped>
.sf-record-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #ffffff;
  border: 1px solid #dddbda;
  border-radius: 3px;
  margin-bottom: 12px;
}
.sf-record-icon {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e8f0fe;
  color: #1589ee;
  font-size: 20px;
}
.sf-record-name {
  font-size: 18px;
  font-weight: 600;
  color: #080707;
  flex: 1;
}
.sf-record-actions {
  display: flex;
  gap: 8px;
}
</style>
