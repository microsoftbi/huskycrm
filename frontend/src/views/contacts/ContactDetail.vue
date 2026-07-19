<template>
  <div class="contact-detail" v-loading="loading">
    <div class="sf-page-header">
      <h2 class="sf-page-title">联系人</h2>
    </div>

    <template v-if="contact">
      <RecordHeader
        :title="`${contact.first_name} ${contact.last_name}`"
        icon-name="user"
        :hide-edit="!can('edit')"
        :hide-delete="!canDelete"
        @edit="$router.push(`/contacts/${contact.id}/edit`)"
        @delete="handleDelete"
      />

      <HighlightsPanel :items="highlightItems" />

      <RecordTabs :tabs="tabs">
        <template #panel-details>
          <RecordSection title="基本信息" :fields="basicFields" />
          <RecordSection title="联系方式" :fields="contactFields" />
          <RecordSection title="系统信息" :fields="systemFields" />
        </template>
        <template #panel-activity>
          <Timeline
            :entries="timelineEntries"
            :loading="timelineLoading"
            :has-more="timelineHasMore"
            @load-more="loadMoreTimeline"
          />
        </template>
      </RecordTabs>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { contactsApi } from '../../api/contacts'
import { auditLogsApi } from '../../api/auditLogs'
import { usePermissions } from '../../composables/usePermissions'
import type { Contact } from '../../types/crm'
import type { TimelineEntry } from '../../types/auditLog'
import RecordHeader from '../../components/record/RecordHeader.vue'
import RecordSection from '../../components/record/RecordSection.vue'
import HighlightsPanel from '../../components/record/HighlightsPanel.vue'
import RecordTabs from '../../components/record/RecordTabs.vue'
import Timeline from '../../components/activity/Timeline.vue'

const route = useRoute()
const router = useRouter()
const { can, canDelete } = usePermissions()
const contact = ref<Contact | null>(null)
const loading = ref(false)

const timelineEntries = ref<TimelineEntry[]>([])
const timelineLoading = ref(false)
const timelinePage = ref(1)
const timelineHasMore = ref(true)

const tabs = computed(() => [
  { key: 'details', label: '详细信息' },
  { key: 'activity', label: '活动' },
])

const highlightItems = computed(() => [
  { label: '邮箱', apiName: 'email', value: contact.value?.email || '-', flex: '1.5' },
  { label: '电话', apiName: 'phone', value: contact.value?.phone || '-', flex: '1' },
  { label: '职位', apiName: 'title', value: contact.value?.title || '-', flex: '1' },
  { label: '部门', apiName: 'department', value: contact.value?.department || '-', flex: '1' },
])

const basicFields = computed(() => [
  { label: '名字', apiName: 'first_name', value: contact.value?.first_name },
  { label: '姓氏', apiName: 'last_name', value: contact.value?.last_name },
  { label: '职位', apiName: 'title', value: contact.value?.title },
  { label: '部门', apiName: 'department', value: contact.value?.department },
])

const contactFields = computed(() => [
  { label: '邮箱', apiName: 'email', value: contact.value?.email },
  { label: '电话', apiName: 'phone', value: contact.value?.phone },
  { label: '手机', apiName: 'mobile_phone', value: contact.value?.mobile_phone },
])

const systemFields = computed(() => [
  { label: '创建时间', apiName: 'created_at', value: contact.value?.created_at },
  { label: '更新时间', apiName: 'updated_at', value: contact.value?.updated_at },
])

async function fetchContact() {
  loading.value = true
  try {
    const { data } = await contactsApi.get(route.params.id as string)
    contact.value = data
  } catch {
    ElMessage.error('联系人不存在')
    router.push('/contacts')
  } finally { loading.value = false }
}

async function handleDelete() {
  if (!contact.value) return
  try {
    await ElMessageBox.confirm(`确定删除 "${contact.value.first_name} ${contact.value.last_name}" 吗？`, '确认删除', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
    await contactsApi.delete(contact.value.id)
    ElMessage.success('删除成功')
    router.push('/contacts')
  } catch { /* cancelled */ }
}

async function loadTimeline() {
  if (!contact.value?.id) return
  timelineLoading.value = true
  try {
    const { data } = await auditLogsApi.getTimeline('contact', contact.value.id, timelinePage.value)
    if (timelinePage.value === 1) {
      timelineEntries.value = data
    } else {
      timelineEntries.value.push(...data)
    }
    timelineHasMore.value = data.length >= 20
  } catch {
    // silent
  } finally {
    timelineLoading.value = false
  }
}

function loadMoreTimeline() {
  timelinePage.value++
  loadTimeline()
}

watch(() => contact.value?.id, (id) => {
  if (id) {
    timelinePage.value = 1
    loadTimeline()
  }
})

onMounted(fetchContact)
</script>

<style scoped>
.contact-detail { max-width: 960px; }
</style>
