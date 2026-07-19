<template>
  <div class="account-detail" v-loading="loading">
    <div class="sf-page-header">
      <h2 class="sf-page-title">账户</h2>
    </div>

    <template v-if="account">
      <!-- Record Header -->
      <RecordHeader
        :title="account.name"
        icon-name="office-building"
        :hide-edit="!can('edit')"
        :hide-delete="!canDelete"
        @edit="$router.push(`/accounts/${account.id}/edit`)"
        @delete="handleDelete"
      />

      <!-- Highlights Panel -->
      <HighlightsPanel :items="highlightItems" />

      <!-- Tabs: Details + Related Lists -->
      <RecordTabs :tabs="tabs">
        <!-- Details Tab -->
        <template #panel-details>
          <RecordSection title="基本信息" :fields="basicFields" />
          <RecordSection title="地址信息" :fields="addressFields" />
          <RecordSection title="系统信息" :fields="systemFields" />
        </template>

        <!-- Contacts Tab -->
        <template #panel-contacts>
          <RelatedList
            title="联系人"
            :total="contactsTotal"
            :items="contacts"
            :columns="contactColumns"
            :loading="contactsLoading"
            :actions="{ view: (r) => `/contacts/${r.id}` }"
            :create-route="`/contacts/new?account_id=${account.id}`"
            create-label="新建联系人"
          />
        </template>

        <!-- Activity Timeline Tab -->
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
import { accountsApi } from '../../api/accounts'
import { contactsApi } from '../../api/contacts'
import { auditLogsApi } from '../../api/auditLogs'
import { usePermissions } from '../../composables/usePermissions'
import type { Account, Contact } from '../../types/crm'
import type { TimelineEntry } from '../../types/auditLog'
import RecordHeader from '../../components/record/RecordHeader.vue'
import RecordSection from '../../components/record/RecordSection.vue'
import HighlightsPanel from '../../components/record/HighlightsPanel.vue'
import RecordTabs from '../../components/record/RecordTabs.vue'
import RelatedList from '../../components/record/RelatedList.vue'
import Timeline from '../../components/activity/Timeline.vue'

const route = useRoute()
const router = useRouter()
const { can, canDelete } = usePermissions()
const account = ref<Account | null>(null)
const loading = ref(false)
const contacts = ref<Contact[]>([])
const contactsTotal = ref(0)
const contactsLoading = ref(false)

const timelineEntries = ref<TimelineEntry[]>([])
const timelineLoading = ref(false)
const timelinePage = ref(1)
const timelineHasMore = ref(true)

const tabs = computed(() => [
  { key: 'details', label: '详细信息' },
  { key: 'contacts', label: '联系人', count: contactsTotal.value },
  { key: 'activity', label: '活动' },
])

const highlightItems = computed(() => [
  { label: '行业', apiName: 'industry', value: account.value?.industry || '-', flex: '1' },
  { label: '电话', apiName: 'phone', value: account.value?.phone || '-', flex: '1' },
  { label: '邮箱', apiName: 'email', value: account.value?.email || '-', flex: '1.5' },
  { label: '城市', apiName: 'city', value: account.value?.billing_city || '-', flex: '1' },
])

const basicFields = computed(() => [
  { label: '行业', apiName: 'industry', value: account.value?.industry },
  { label: '电话', apiName: 'phone', value: account.value?.phone },
  { label: '邮箱', apiName: 'email', value: account.value?.email },
  { label: '网站', apiName: 'website', value: account.value?.website },
  { label: '描述', apiName: 'description', value: account.value?.description },
])

const addressFields = computed(() => [
  { label: '街道', apiName: 'billing_street', value: account.value?.billing_street },
  { label: '城市', apiName: 'billing_city', value: account.value?.billing_city },
  { label: '省份', apiName: 'billing_state', value: account.value?.billing_state },
  { label: '邮编', apiName: 'billing_zip', value: account.value?.billing_zip },
  { label: '国家', apiName: 'billing_country', value: account.value?.billing_country },
])

const systemFields = computed(() => [
  { label: '创建时间', apiName: 'created_at', value: account.value?.created_at },
  { label: '更新时间', apiName: 'updated_at', value: account.value?.updated_at },
])

const contactColumns = [
  { prop: 'first_name', label: '名字', width: 100 },
  { prop: 'last_name', label: '姓氏', width: 100 },
  { prop: 'email', label: '邮箱', minWidth: 200 },
  { prop: 'phone', label: '电话', width: 140 },
  { prop: 'title', label: '职位', width: 150 },
]

async function fetchAccount() {
  loading.value = true
  try {
    const { data } = await accountsApi.get(route.params.id as string)
    account.value = data
    // Load related contacts
    fetchContacts()
  } catch {
    ElMessage.error('账户不存在')
    router.push('/accounts')
  } finally {
    loading.value = false
  }
}

async function fetchContacts() {
  contactsLoading.value = true
  try {
    const { data } = await contactsApi.list({ account_id: route.params.id as string, page_size: 50 })
    contacts.value = data.items
    contactsTotal.value = data.total
  } finally {
    contactsLoading.value = false
  }
}

async function handleDelete() {
  if (!account.value) return
  try {
    await ElMessageBox.confirm(`确定删除账户 "${account.value.name}" 吗？`, '确认删除', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
    await accountsApi.delete(account.value.id)
    ElMessage.success('删除成功')
    router.push('/accounts')
  } catch { /* cancelled */ }
}

async function loadTimeline() {
  if (!account.value?.id) return
  timelineLoading.value = true
  try {
    const { data } = await auditLogsApi.getTimeline('account', account.value.id, timelinePage.value)
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

watch(() => account.value?.id, (id) => {
  if (id) {
    timelinePage.value = 1
    loadTimeline()
  }
})

onMounted(fetchAccount)
</script>

<style scoped>
.account-detail { max-width: 960px; }
</style>
