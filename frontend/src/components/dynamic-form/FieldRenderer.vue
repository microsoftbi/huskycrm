<template>
  <div class="field-renderer">
    <el-form-item
      v-if="field.field_type === 'text' || field.field_type === 'email' || field.field_type === 'phone' || field.field_type === 'url'"
      :label="field.label"
      :required="field.is_required"
    >
      <el-input v-model="modelValue[field.api_name]" :placeholder="`请输入${field.label}`" />
    </el-form-item>

    <el-form-item
      v-else-if="field.field_type === 'textarea'"
      :label="field.label"
      :required="field.is_required"
    >
      <el-input v-model="modelValue[field.api_name]" type="textarea" :rows="3" :placeholder="`请输入${field.label}`" />
    </el-form-item>

    <el-form-item
      v-else-if="field.field_type === 'number' || field.field_type === 'integer'"
      :label="field.label"
      :required="field.is_required"
    >
      <el-input-number
        v-model="modelValue[field.api_name]"
        :precision="field.field_type === 'number' ? 2 : 0"
        :min="0"
        style="width:100%"
      />
    </el-form-item>

    <el-form-item
      v-else-if="field.field_type === 'boolean'"
      :label="field.label"
    >
      <el-switch v-model="modelValue[field.api_name]" />
    </el-form-item>

    <el-form-item
      v-else-if="field.field_type === 'date'"
      :label="field.label"
      :required="field.is_required"
    >
      <el-date-picker
        v-model="modelValue[field.api_name]"
        type="date"
        :placeholder="`选择${field.label}`"
        style="width:100%"
        value-format="YYYY-MM-DD"
      />
    </el-form-item>

    <el-form-item
      v-else-if="field.field_type === 'picklist'"
      :label="field.label"
      :required="field.is_required"
    >
      <el-select v-model="modelValue[field.api_name]" :placeholder="`选择${field.label}`" style="width:100%">
        <el-option
          v-for="opt in field.picklist_values || []"
          :key="opt"
          :label="opt"
          :value="opt"
        />
      </el-select>
    </el-form-item>

    <el-form-item
      v-else
      :label="field.label"
    >
      <el-input v-model="modelValue[field.api_name]" :placeholder="`请输入${field.label}`" />
    </el-form-item>
  </div>
</template>

<script setup lang="ts">
import type { CustomFieldDef } from '../../types/crm'

const props = defineProps<{
  field: CustomFieldDef
  modelValue: Record<string, any>
}>()

defineEmits(['update:modelValue'])
</script>