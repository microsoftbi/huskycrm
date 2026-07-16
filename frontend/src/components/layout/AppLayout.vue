<template>
  <div class="app-root">
    <!-- App Header -->
    <Header />

    <!-- Nav Tabs -->
    <NavTabs />

    <!-- Main Content -->
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import Header from './Header.vue'
import NavTabs from './NavTabs.vue'
import { useAuth } from '../../composables/useAuth'

useAuth()
</script>

<style scoped>
.app-root {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.app-main {
  flex: 1;
  overflow-y: auto;
  background: #f4f6f9;
  padding: 16px 20px 32px;
}
</style>
