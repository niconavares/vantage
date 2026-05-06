<template>
  <div class="space-y-5 animate-entry">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="page-title">Credenciales</h1>
        <p class="page-subtitle">{{ credentials.length }} credenciales obtenidas</p>
      </div>
      <div class="flex gap-2">
        <button @click="showPwd = !showPwd" class="btn-ghost text-xs">
          {{ showPwd ? '🙈 Ocultar' : '👁 Revelar' }} passwords
        </button>
      </div>
    </div>

    <!-- Service stats -->
    <div v-if="serviceStats.length" class="flex gap-2 flex-wrap">
      <div v-for="s in serviceStats" :key="s.service"
        class="flex items-center gap-2 px-3 py-1.5 rounded-xl cursor-pointer transition-all"
        :style="serviceFilter === s.service
          ? 'background:rgba(0,212,255,0.1);border:1px solid rgba(0,212,255,0.3);'
          : 'background:rgba(0,0,0,0.3);border:1px solid #1e2d3d;'"
        @click="serviceFilter = serviceFilter === s.service ? '' : s.service">
        <span class="font-mono text-xs font-bold text-cyan uppercase">{{ s.service }}</span>
        <span class="text-xs font-bold" style="color:#fff;font-family:'Rajdhani',sans-serif;">{{ s.count }}</span>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex gap-3 flex-wrap items-center">
      <div class="relative">
        <input v-model="search" type="text" placeholder="Buscar usuario, host..." class="input max-w-xs pl-8" />
        <svg class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5" style="color:#4b6277;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
      </div>
      <label class="flex items-center gap-2 px-3 py-2 rounded-xl cursor-pointer transition-all"
        :style="onlyValid ? 'background:rgba(0,255,157,0.08);border:1px solid rgba(0,255,157,0.2);' : 'background:rgba(0,0,0,0.3);border:1px solid #1e2d3d;'">
        <input type="checkbox" v-model="onlyValid" class="accent-cyan" />
        <span class="text-xs font-bold uppercase" :style="onlyValid ? 'color:#00ff9d;' : 'color:#4b6277;'" style="font-family:'Rajdhani',sans-serif;letter-spacing:0.08em;">Solo válidas</span>
      </label>
    </div>

    <!-- Table -->
    <div class="card p-0 overflow-hidden">
      <table class="vtable w-full">
        <thead>
          <tr>
            <th class="pl-5">Servicio</th>
            <th>Host</th>
            <th>Puerto</th>
            <th>Usuario</th>
            <th>Contraseña / Hash</th>
            <th>Válida</th>
            <th class="pr-5">Detectada</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="7" class="text-center py-16" style="color:#4b6277;">Cargando...</td></tr>
          <tr v-else-if="!filtered.length">
            <td colspan="7" class="text-center py-16">
              <div class="text-3xl mb-2 opacity-30">🔑</div>
              <div style="color:#4b6277;">Sin credenciales encontradas</div>
            </td>
          </tr>
          <tr v-for="c in filtered" :key="c.id">
            <td class="pl-5">
              <span class="font-mono text-xs font-bold text-cyan uppercase px-2 py-0.5 rounded" style="background:rgba(0,212,255,0.08);border:1px solid rgba(0,212,255,0.15);">{{ c.service }}</span>
            </td>
            <td><span class="font-mono text-xs" style="color:#c9d8e5;">{{ hostMap[c.host] || c.host }}</span></td>
            <td><span v-if="c.port" class="font-mono text-xs" style="color:#4b6277;">:{{ portMap[c.port] || '?' }}</span><span v-else style="color:#2d4356;">—</span></td>
            <td><span class="font-mono text-sm font-bold" style="color:#fff;">{{ c.username }}</span></td>
            <td>
              <span v-if="c.password" class="font-mono text-sm" style="color:#00ff9d;">
                {{ showPwd ? c.password : '••••••••' }}
              </span>
              <div v-else-if="c.hash_value" class="font-mono text-xs" style="color:#f59e0b;">
                <span style="color:#4b6277;">[{{ c.hash_type }}]</span> {{ showPwd ? c.hash_value : c.hash_value.slice(0,16)+'...' }}
              </div>
              <span v-else style="color:#2d4356;">—</span>
            </td>
            <td>
              <span v-if="c.valid" class="text-xs font-bold uppercase px-2 py-0.5 rounded" style="background:rgba(0,255,157,0.08);border:1px solid rgba(0,255,157,0.2);color:#00ff9d;font-family:'Rajdhani',sans-serif;">✓ VÁLIDA</span>
              <span v-else class="text-xs" style="color:#2d4356;">✗</span>
            </td>
            <td class="pr-5 text-xs" style="color:#4b6277;font-family:'JetBrains Mono',monospace;font-size:11px;">{{ formatDate(c.found_at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/composables/api'

const credentials  = ref([])
const loading      = ref(true)
const search       = ref('')
const serviceFilter = ref('')
const onlyValid    = ref(false)
const showPwd      = ref(false)
const hostMap      = ref({})
const portMap      = ref({})

const services = computed(() => [...new Set(credentials.value.map(c => c.service))].sort())
const serviceStats = computed(() => {
  const map = {}
  credentials.value.forEach(c => { map[c.service] = (map[c.service] || 0) + 1 })
  return Object.entries(map).map(([service, count]) => ({ service, count })).sort((a,b) => b.count - a.count)
})

const filtered = computed(() => {
  let list = credentials.value
  if (serviceFilter.value) list = list.filter(c => c.service === serviceFilter.value)
  if (onlyValid.value)     list = list.filter(c => c.valid)
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(c => c.username.toLowerCase().includes(q) || (hostMap.value[c.host] || '').includes(q))
  }
  return list
})

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' })
}

onMounted(async () => {
  try {
    const [credsRes, hostsRes, portsRes] = await Promise.all([
      api.get('/credentials/?page_size=500'),
      api.get('/hosts/?page_size=500'),
      api.get('/ports/?page_size=2000'),
    ])
    credentials.value = credsRes.data.results || credsRes.data
    ;(hostsRes.data.results || hostsRes.data).forEach(h => { hostMap.value[h.id] = h.ip_address })
    ;(portsRes.data.results || portsRes.data).forEach(p => { portMap.value[p.id] = p.number })
  } finally { loading.value = false }
})
</script>
