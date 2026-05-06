<template>
  <div class="min-h-screen bg-bg">
    <template v-if="auth.token">
      <Sidebar />
      <main class="ml-60 min-h-screen">
        <TopBar />
        <div class="p-6">
          <RouterView />
        </div>
      </main>
    </template>
    <template v-else>
      <RouterView />
    </template>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import Sidebar from '@/components/layout/Sidebar.vue'
import TopBar  from '@/components/layout/TopBar.vue'
const auth = useAuthStore()
</script>
