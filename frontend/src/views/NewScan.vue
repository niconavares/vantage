<template>
  <div class="max-w-3xl animate-entry">
    <div class="flex items-center gap-4 mb-8">
      <RouterLink :to="`/engagements/${id}`" class="btn-ghost px-3 py-2">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
      </RouterLink>
      <div>
        <h1 class="page-title">Lanzar Operación</h1>
        <p class="page-subtitle">Configura y ejecuta un nuevo escaneo</p>
      </div>
    </div>

    <form @submit.prevent="launch" class="space-y-5">

      <!-- Scan type selector -->
      <div class="card">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-1 h-5 rounded-full bg-cyan"></div>
          <span class="section-title">Tipo de Operación</span>
        </div>
        <div class="grid grid-cols-3 gap-2">
          <button v-for="t in SCAN_TYPES" :key="t.id" type="button"
            @click="form.scan_type = t.id"
            class="flex flex-col gap-2 p-3 rounded-xl border transition-all text-left"
            :style="form.scan_type === t.id
              ? 'border-color:rgba(0,212,255,0.4);background:rgba(0,212,255,0.05);box-shadow:0 0 15px rgba(0,212,255,0.08);'
              : 'border-color:#1e2d3d;background:rgba(0,0,0,0.2);'">
            <span class="text-2xl">{{ t.icon }}</span>
            <div>
              <div class="text-sm font-bold" :style="form.scan_type === t.id ? 'color:#00d4ff;font-family:Rajdhani,sans-serif;letter-spacing:0.04em;' : 'color:#8ba5bc;font-family:Rajdhani,sans-serif;letter-spacing:0.04em;'">{{ t.label }}</div>
              <div class="text-xs mt-0.5" style="color:#4b6277;">{{ t.desc }}</div>
            </div>
            <!-- Selected mark -->
            <div v-if="form.scan_type === t.id" class="absolute top-2 right-2 w-4 h-4 rounded-full bg-cyan flex items-center justify-center">
              <svg class="w-2.5 h-2.5" style="color:#060910;" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
            </div>
          </button>
        </div>
      </div>

      <!-- Targets -->
      <div class="card">
        <div class="flex items-center gap-2 mb-3">
          <div class="w-1 h-5 rounded-full bg-cyan"></div>
          <span class="section-title">Objetivos</span>
        </div>
        <p class="text-xs mb-3" style="color:#4b6277;">Un target por línea: CIDR, IP, rango o hostname</p>
        <textarea v-model="targetsText" rows="4" class="input font-mono text-sm" style="resize:none;"
          placeholder="192.168.1.0/24&#10;10.0.0.1&#10;172.16.0.0/12"></textarea>
        <!-- Quick targets -->
        <div class="flex gap-2 mt-2 flex-wrap">
          <button v-for="q in quickTargets" :key="q" type="button"
            @click="targetsText = q"
            class="text-xs px-2 py-1 rounded-lg transition-all" style="background:rgba(0,212,255,0.06);border:1px solid rgba(0,212,255,0.15);color:#00d4ff;font-family:'JetBrains Mono',monospace;">
            {{ q }}
          </button>
        </div>
      </div>

      <!-- Options grid -->
      <div class="card">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-1 h-5 rounded-full bg-cyan"></div>
          <span class="section-title">Configuración Avanzada</span>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block mb-1.5 text-xs uppercase tracking-wider" style="color:#4b6277;font-family:'Rajdhani',sans-serif;">Timing nmap</label>
            <select v-model="form.config.timing" class="input">
              <option value="T1">T1 — Paranoico (stealth)</option>
              <option value="T2">T2 — Discreto</option>
              <option value="T3">T3 — Normal</option>
              <option value="T4">T4 — Agresivo (recomendado)</option>
              <option value="T5">T5 — Insano</option>
            </select>
          </div>
          <div>
            <label class="block mb-1.5 text-xs uppercase tracking-wider" style="color:#4b6277;font-family:'Rajdhani',sans-serif;">Puertos</label>
            <select v-model="form.config.ports" class="input">
              <option value="top-100">Top 100 (rápido)</option>
              <option value="top-1000">Top 1000 (estándar)</option>
              <option value="1-65535">Todos — 1-65535 (lento)</option>
            </select>
          </div>
          <div class="flex items-center gap-3 p-3 rounded-xl" style="background:rgba(0,0,0,0.3);border:1px solid #1e2d3d;">
            <input type="checkbox" id="udp" v-model="form.config.udp" class="w-4 h-4 rounded accent-cyan" />
            <div>
              <label for="udp" class="text-sm font-semibold cursor-pointer" style="color:#8ba5bc;font-family:'Rajdhani',sans-serif;">Scan UDP</label>
              <div class="text-xs" style="color:#4b6277;">Top 100 puertos UDP</div>
            </div>
          </div>
          <div class="flex items-center gap-3 p-3 rounded-xl" style="background:rgba(0,0,0,0.3);border:1px solid #1e2d3d;">
            <input type="checkbox" id="os" v-model="form.config.os_detection" class="w-4 h-4 rounded accent-cyan" />
            <div>
              <label for="os" class="text-sm font-semibold cursor-pointer" style="color:#8ba5bc;font-family:'Rajdhani',sans-serif;">Detección OS</label>
              <div class="text-xs" style="color:#4b6277;">nmap -O --osscan-guess</div>
            </div>
          </div>
        </div>

        <div v-if="form.scan_type === 'vuln' || form.scan_type === 'full'" class="mt-4">
          <label class="block mb-2 text-xs uppercase tracking-wider" style="color:#4b6277;font-family:'Rajdhani',sans-serif;">Severidades a detectar</label>
          <div class="flex gap-2 flex-wrap">
            <label v-for="s in SEVERITIES" :key="s.id" class="flex items-center gap-2 cursor-pointer px-3 py-1.5 rounded-lg border transition-all"
              :style="form.config.severity?.includes(s.id) ? `border-color:${s.color}30;background:${s.color}10;` : 'border-color:#1e2d3d;'">
              <input type="checkbox" :value="s.id" v-model="form.config.severity" class="accent-cyan" />
              <span :class="`badge-${s.id}`">{{ s.label }}</span>
            </label>
          </div>
        </div>
      </div>

      <!-- ETA warning for full scan -->
      <div v-if="form.scan_type === 'full'" class="flex items-start gap-3 px-4 py-3 rounded-xl" style="background:rgba(245,158,11,0.06);border:1px solid rgba(245,158,11,0.2);">
        <svg class="w-5 h-5 text-yellow flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
        <div>
          <div class="text-sm font-bold text-yellow" style="font-family:'Rajdhani',sans-serif;letter-spacing:0.04em;">Full Audit — tiempo estimado: 20-60 min</div>
          <div class="text-xs mt-0.5" style="color:#4b6277;">Ejecuta todos los módulos: discovery, puertos 1-65535, SSL, SMB, SNMP, AD, brute force y nuclei.</div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex gap-3">
        <button type="submit" :disabled="loading || !targetsText.trim()" class="btn-primary flex-1 justify-center" style="height:48px;font-size:15px;">
          <svg v-if="loading" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          {{ loading ? 'LANZANDO OPERACIÓN...' : 'INICIAR SCAN' }}
        </button>
        <RouterLink :to="`/engagements/${id}`" class="btn-ghost px-6">Cancelar</RouterLink>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/composables/api'

const route   = useRoute()
const router  = useRouter()
const id      = route.params.id
const loading = ref(false)
const quickTargets = ref([])

const form = reactive({
  engagement: id,
  scan_type:  'full',
  targets:    [],
  config: {
    timing: 'T4', ports: 'top-1000', udp: false,
    os_detection: true, severity: ['critical', 'high', 'medium'],
  }
})
const targetsText = ref('')

const SCAN_TYPES = [
  { id: 'full',      label: 'Full Audit',       icon: '🎯', desc: 'Todos los módulos' },
  { id: 'discovery', label: 'Discovery',        icon: '🔭', desc: 'Hosts vivos' },
  { id: 'port',      label: 'Port Scan',        icon: '🔌', desc: 'TCP/UDP completo' },
  { id: 'vuln',      label: 'Vuln Scan',        icon: '🧪', desc: 'Nuclei + CVEs' },
  { id: 'ssl',       label: 'SSL/TLS',          icon: '🔐', desc: 'Certs y cifrados' },
  { id: 'smb',       label: 'SMB Audit',        icon: '🪟', desc: 'EternalBlue / SMB' },
  { id: 'ad',        label: 'Active Directory', icon: '🏰', desc: 'LDAP / Kerberos' },
  { id: 'brute',     label: 'Brute Force',      icon: '🔑', desc: 'Default credentials' },
  { id: 'snmp',      label: 'SNMP',             icon: '📡', desc: 'Community strings' },
]
const SEVERITIES = [
  { id: 'critical', label: 'Critical', color: '#ff3864' },
  { id: 'high',     label: 'High',     color: '#ff6b35' },
  { id: 'medium',   label: 'Medium',   color: '#f59e0b' },
  { id: 'low',      label: 'Low',      color: '#4cc9f0' },
]

onMounted(async () => {
  try {
    const res = await api.get(`/engagements/${id}/`)
    const targets = res.data.targets || []
    quickTargets.value = targets.map(t => t.value).slice(0, 4)
    if (targets.length === 1) targetsText.value = targets[0].value
  } catch {}
})

async function launch() {
  form.targets = targetsText.value.split('\n').map(t => t.trim()).filter(Boolean)
  loading.value = true
  try {
    const res = await api.post('/scan-jobs/', form)
    router.push(`/scan-jobs`)
  } catch (e) {
    alert('Error: ' + JSON.stringify(e.response?.data))
  } finally {
    loading.value = false
  }
}
</script>
