<template>
  <RouterLink :to="to"
    class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 group relative"
    :class="isActive
      ? 'nav-active'
      : 'text-muted hover:text-gray-200 hover:bg-white/[0.04]'">
    <!-- Active indicator line -->
    <span v-if="isActive" class="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-cyan rounded-r-full" style="left:-1px"></span>
    <svg class="w-4 h-4 flex-shrink-0 transition-all" :class="isActive ? 'text-cyan' : 'text-muted group-hover:text-gray-300'" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" :d="iconPath" />
    </svg>
    <span class="flex-1 font-display font-semibold tracking-wide" style="font-family:'Rajdhani',sans-serif;letter-spacing:0.04em;">{{ label }}</span>
    <span v-if="badge && badge > 0"
      class="text-[10px] font-bold px-1.5 py-0.5 rounded-full tabular-nums"
      :class="badgeColor === 'red' ? 'bg-red/20 text-red border border-red/20' : 'bg-cyan/15 text-cyan border border-cyan/20'">
      {{ badge > 99 ? '99+' : badge }}
    </span>
  </RouterLink>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({ to: String, icon: String, label: String, badge: Number, badgeColor: String })
const route = useRoute()
const isActive = computed(() => route.path === props.to || (props.to !== '/' && route.path.startsWith(props.to)))

const ICONS = {
  'grid':        'M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z',
  'briefcase':   'M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
  'shield-alert':'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z',
  'key':         'M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z',
  'activity':    'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
  'cpu':         'M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18',
}
const iconPath = computed(() => ICONS[props.icon] || ICONS['grid'])
</script>
