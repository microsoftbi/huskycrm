<template>
  <div class="global-search" ref="searchRef">
    <el-input
      v-model="query"
      placeholder="搜索账户、联系人、商机..."
      size="small"
      clearable
      :prefix-icon="SearchIcon"
      @input="handleInput"
      @keyup.enter="handleEnter"
      @focus="showPanel = true"
      @keydown.escape="showPanel = false"
    />

    <Transition name="search-fade">
      <div v-if="showPanel && query.length > 0" class="search-panel">
        <div v-if="loading" class="search-loading">
          <el-icon class="is-loading" :size="20"><loading /></el-icon>
        </div>
        <template v-else>
          <div v-if="hasResults" class="search-results">
            <div v-for="(items, type) in groupedResults" :key="type">
              <div v-if="items.length > 0" class="search-group">
                <div class="search-group-label">{{ groupLabel(type) }}</div>
                <div
                  v-for="item in items"
                  :key="item.id"
                  class="search-item"
                  @click="navigateTo(type, item.id)"
                >
                  <el-icon :size="14" class="search-item-icon">
                    <component :is="iconFor(type)" />
                  </el-icon>
                  <span class="search-item-name">{{ item.name }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="search-no-results">未找到相关结果</div>
        </template>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search as SearchIcon, Loading } from '@element-plus/icons-vue'
import { OfficeBuilding, User, TrendCharts, Box, Phone } from '@element-plus/icons-vue'
import { searchApi } from '../../api/search'
import type { SearchResults } from '../../types/search'

const router = useRouter()
const query = ref('')
const loading = ref(false)
const showPanel = ref(false)
const results = ref<SearchResults>({ accounts: [], contacts: [], opportunities: [], products: [], events: [], custom_objects: {} })
const searchRef = ref<HTMLElement | null>(null)
let debounceTimer: number | null = null

const ICONS: Record<string, any> = {
  accounts: OfficeBuilding,
  contacts: User,
  opportunities: TrendCharts,
  products: Box,
  events: Phone,
}

const GROUP_LABELS: Record<string, string> = {
  accounts: '账户',
  contacts: '联系人',
  opportunities: '销售机会',
  products: '产品',
  events: '拜访',
}

const groupedResults = computed(() => results.value)

const hasResults = computed(() => {
  for (const key of Object.keys(results.value)) {
    if (key === 'custom_objects') {
      for (const val of Object.values((results.value as any).custom_objects)) {
        if (Array.isArray(val) && val.length > 0) return true
      }
    } else {
      if ((results.value as any)[key]?.length > 0) return true
    }
  }
  return false
})

function iconFor(type: string): any {
  return ICONS[type] || OfficeBuilding
}

function groupLabel(type: string): string {
  return GROUP_LABELS[type] || type
}

function handleInput() {
  if (debounceTimer) clearTimeout(debounceTimer)
  if (!query.value.trim()) {
    showPanel.value = false
    return
  }
  debounceTimer = window.setTimeout(doSearch, 300)
}

async function doSearch() {
  const q = query.value.trim()
  if (!q) return
  loading.value = true
  try {
    const { data } = await searchApi.search(q)
    results.value = data
  } catch {
    // silent
  } finally {
    loading.value = false
  }
}

function handleEnter() {
  if (query.value.trim()) {
    showPanel.value = false
    router.push(`/accounts?search=${encodeURIComponent(query.value.trim())}`)
  }
}

function navigateTo(type: string, id: string) {
  showPanel.value = false
  query.value = ''
  const routes: Record<string, string> = {
    accounts: `/accounts/${id}`,
    contacts: `/contacts/${id}`,
    opportunities: `/opportunities/${id}`,
    products: `/products/${id}`,
    events: `/events/${id}`,
  }
  const path = routes[type]
  if (path) router.push(path)
}

// Keyboard shortcut: Ctrl+K
function handleKeydown(e: KeyboardEvent) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault()
    const input = searchRef.value?.querySelector('input')
    input?.focus()
  }
}

// Click outside to close
function handleClickOutside(e: MouseEvent) {
  if (searchRef.value && !searchRef.value.contains(e.target as Node)) {
    showPanel.value = false
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.global-search { position: relative; width: 100%; }
.search-panel {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 4px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  z-index: 2000;
  max-height: 400px;
  overflow-y: auto;
}
.search-loading { padding: 20px; text-align: center; }
.search-no-results { padding: 30px; text-align: center; color: #909399; }
.search-group { padding: 4px 0; }
.search-group-label {
  font-size: 11px; font-weight: 700; color: #909399;
  text-transform: uppercase; padding: 4px 12px; letter-spacing: 0.5px;
}
.search-item {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 12px; cursor: pointer; font-size: 13px;
  transition: background 0.1s;
}
.search-item:hover { background: #f0f7ff; }
.search-item-icon { color: #706e6b; flex-shrink: 0; }
.search-item-name { color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.search-fade-enter-active, .search-fade-leave-active { transition: opacity 0.15s; }
.search-fade-enter-from, .search-fade-leave-to { opacity: 0; }
</style>