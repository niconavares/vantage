<template>
  <aside class="fixed left-0 top-0 h-full w-60 flex flex-col z-50" style="background:linear-gradient(180deg,#080c14 0%,#060910 100%);border-right:1px solid #1e2d3d;">

    <!-- Logo -->
    <div class="px-5 py-5 border-b" style="border-color:#1e2d3d;">
      <div class="flex items-center gap-3">
        <!-- Icon -->
        <div class="w-9 h-9 rounded-lg flex items-center justify-center relative overflow-hidden glow-cyan" style="background:linear-gradient(135deg,rgba(0,212,255,0.15),rgba(0,212,255,0.05));border:1px solid rgba(0,212,255,0.3);">
          <svg class="w-5 h-5 text-cyan" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"/>
          </svg>
        </div>
        <div>
          <div class="text-white font-bold leading-none" style="font-family:'Rajdhani',sans-serif;font-size:22px;letter-spacing:0.08em;">VANTAGE</div>
          <div class="text-[9px] uppercase tracking-widest" style="color:#4b6277;font-family:'Rajdhani',sans-serif;letter-spacing:0.18em;">NETWORK AUDIT</div>
        </div>
      </div>
    </div>

    <!-- Nav -->
    <nav class="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">

      <NavItem to="/" icon="grid" label="Dashboard" />
      <NavItem to="/engagements" icon="briefcase" label="Engagements" />

      <div class="pt-5 pb-2 px-3">
        <div style="font-family:'Rajdhani',sans-serif;font-size:9px;letter-spacing:0.18em;color:#2d4356;font-weight:700;text-transform:uppercase;">HALLAZGOS</div>
      </div>
      <NavItem to="/vulns" icon="shield-alert" label="Vulnerabilidades" :badge="critCount" badge-color="red" />
      <NavItem to="/credentials" icon="key" label="Credenciales" />

      <div class="pt-5 pb-2 px-3">
        <div style="font-family:'Rajdhani',sans-serif;font-size:9px;letter-spacing:0.18em;color:#2d4356;font-weight:700;text-transform:uppercase;">OPERACIONES</div>
      </div>
      <NavItem to="/scan-jobs" icon="activity" label="Scan Jobs" :badge="activeJobs" badge-color="cyan" />
      <NavItem to="/ai-assistant" icon="cpu" label="AI Assistant" />
    </nav>

    <!-- System status -->
    <div class="px-4 py-3 mx-3 mb-3 rounded-xl" style="background:rgba(0,0,0,0.3);border:1px solid #1e2d3d;">
      <div class="text-[9px] uppercase tracking-widest mb-2" style="color:#2d4356;font-family:'Rajdhani',sans-serif;letter-spacing:0.15em;">SISTEMA</div>
      <div class="flex items-center justify-between text-xs mb-1.5">
        <span style="color:#4b6277;">Celery</span>
        <div class="flex items-center gap-1.5">
          <span class="w-1.5 h-1.5 rounded-full" :class="celeryOk ? 'bg-green' : 'bg-red'"></span>
          <span :class="celeryOk ? 'text-green' : 'text-red'" style="font-family:'Rajdhani',sans-serif;font-size:11px;font-weight:600;">{{ celeryOk ? 'ONLINE' : 'OFFLINE' }}</span>
        </div>
      </div>
      <div class="flex items-center justify-between text-xs">
        <span style="color:#4b6277;">API</span>
        <div class="flex items-center gap-1.5">
          <span class="w-1.5 h-1.5 rounded-full bg-green"></span>
          <span class="text-green" style="font-family:'Rajdhani',sans-serif;font-size:11px;font-weight:600;">ONLINE</span>
        </div>
      </div>
    </div>

    <!-- User -->
    <div class="px-3 pb-4 border-t pt-3" style="border-color:#1e2d3d;">
      <div class="flex items-center gap-3 px-2 mb-2">
        <div class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold" style="background:linear-gradient(135deg,rgba(0,212,255,0.15),rgba(0,212,255,0.05));border:1px solid rgba(0,212,255,0.2);color:#00d4ff;font-family:'Rajdhani',sans-serif;">
          {{ auth.user?.username?.slice(0,2).toUpperCase() || 'OP' }}
        </div>
        <div class="flex-1 min-w-0">
          <div class="text-xs font-semibold text-white truncate" style="font-family:'Rajdhani',sans-serif;letter-spacing:0.04em;">{{ auth.user?.username || 'Operator' }}</div>
          <div class="text-[9px] uppercase tracking-wider" style="color:#4b6277;font-family:'Rajdhani',sans-serif;">ANALISTA</div>
        </div>
      </div>
      <button @click="auth.logout()"
        class="w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-all text-xs"
        style="color:#4b6277;font-family:'Rajdhani',sans-serif;font-weight:600;letter-spacing:0.05em;"
        onmouseover="this.style.color='#ff3864';this.style.background='rgba(255,56,100,0.06)'"
        onmouseout="this.style.color='#4b6277';this.style.background='transparent'">
        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
        </svg>
        CERRAR SESIÓN
      </button>
    </div>
  </aside>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import NavItem from './NavItem.vue'
import api from '@/composables/api'

const auth       = useAuthStore()
const critCount  = ref(0)
const activeJobs = ref(0)
const celeryOk   = ref(true)

async function poll() {
  try {
    const [vulnRes, jobRes] = await Promise.all([
      api.get('/vulns/?severity=critical&status=open&page_size=1'),
      api.get('/scan-jobs/?status=1&page_size=1'),
    ])
    critCount.value  = vulnRes.data.count || 0
    activeJobs.value = jobRes.data.count  || 0
    celeryOk.value   = true
  } catch { celeryOk.value = false }
}

onMounted(() => { poll(); setInterval(poll, 15000) })
</script>
