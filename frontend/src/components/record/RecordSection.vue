<template>
  <div class="sf-field-section">
    <div class="sf-field-section-title">{{ title }}</div>
    <div class="sf-field-row">
      <div v-for="field in fields" :key="field.label" class="sf-field">
        <div class="sf-field-label">{{ field.label }}</div>
        <div class="sf-field-value">
          <slot :name="field.apiName" :value="field.value">
            {{ formatValue(field) }}
          </slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface FieldDef {
  label: string
  apiName: string
  value: any
  type?: string
}

defineProps<{
  title: string
  fields: FieldDef[]
}>()

function formatValue(field: FieldDef): string {
  if (field.value === null || field.value === undefined) return '-'
  if (field.type === 'currency') {
    return `¥${Number(field.value).toLocaleString()}`
  }
  return String(field.value)
}
</script>

<style scoped>
.sf-field-section {
  background: #ffffff;
  border: 1px solid #dddbda;
  border-radius: 3px;
  margin-bottom: 12px;
}
.sf-field-section-title {
  padding: 10px 14px;
  font-size: 12px;
  font-weight: 700;
  color: #514f4d;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  border-bottom: 1px solid #dddbda;
  background: #fafafa;
}
.sf-field-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0;
}
.sf-field {
  padding: 8px 14px;
  border-bottom: 1px solid #f3f2f2;
}
.sf-field:nth-child(even) {
  border-left: 1px solid #f3f2f2;
}
.sf-field-label {
  font-size: 11px;
  color: #706e6b;
  margin-bottom: 2px;
  font-weight: 400;
}
.sf-field-value {
  font-size: 13px;
  color: #080707;
  font-weight: 400;
}
</style>
