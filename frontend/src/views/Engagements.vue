<template>
  <div class="space-y-6 animate-entry">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="page-title">Engagements</h1>
        <p class="page-subtitle">Proyectos de auditoría activos y archivados</p>
      </div>
      <button @click="showModal = true" class="btn-primary">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
        Nuevo Engagement
      </button>
    </div>

    <!-- Filters -->
    <div class="flex gap-3 flex-wrap">
      <div class="relative">
        <input v-model="search" type="text" placeholder="Buscar cliente o proyecto..." class="input pl-8 max-w-xs" />
        <svg class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5" style="color:#4b6277;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
      </div>
      <select v-model="statusFilter" class="input max-w-[170px]">
        <option value="">Todos los estados</option>
        <option v-for="s in STATUS_OPTS" :key="s.value" :value="s.value">{{ s.label }}</option>
      </select>
    </div>

    <!-- Grid -->
    <div v-if="filtered.length" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 animate-entry-1">
      <div v-for="(eng, i) in filtered" :key="eng.id" class="relative group">
        <!-- Delete button -->
        <button @click.prevent="deleteEngagement(eng)"
          class="absolute top-3 right-3 z-10 w-7 h-7 rounded-lg flex items-center justify-center transition-all hover:scale-110"
          style="color:#ff3864;background:rgba(255,56,100,0.12);border:1px solid rgba(255,56,100,0.25);"
          title="Eliminar engagement">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
        </button>
        <RouterLink
        :to="`/engagements/${eng.id}`"
        class="card cursor-pointer block transition-all duration-200"
        style="animation:slide-up 0.4s both;"
        :style="`animation-delay:${i*40}ms`"
        onmouseover="this.style.borderColor='rgba(0,212,255,0.25)';this.style.transform='translateY(-2px)'"
        onmouseout="this.style.borderColor='#1e2d3d';this.style.transform='translateY(0)'">

        <!-- Top: client + status -->
        <div class="flex items-start justify-between mb-3">
          <div class="flex-1 min-w-0 pr-3">
            <div class="text-[10px] uppercase tracking-widest mb-1" style="color:#4b6277;font-family:'Rajdhani',sans-serif;letter-spacing:0.14em;">{{ eng.client }}</div>
            <div class="text-base font-bold text-white truncate group-hover:text-cyan transition-colors" style="font-family:'Rajdhani',sans-serif;letter-spacing:0.03em;">{{ eng.name }}</div>
          </div>
          <StatusBadge :status="eng.status" class="flex-shrink-0" />
        </div>

        <!-- Threat level bar -->
        <div class="mb-3">
          <div class="flex items-center justify-between mb-1">
            <span class="text-[10px] uppercase tracking-wider" style="color:#4b6277;font-family:'Rajdhani',sans-serif;">Nivel de Amenaza</span>
            <span class="text-xs font-bold font-mono" :style="`color:${threatColor(eng)}`">{{ threatLabel(eng) }}</span>
          </div>
          <div class="h-1 rounded-full" style="background:#1e2d3d;">
            <div class="h-full rounded-full transition-all duration-700"
              :style="`width:${threatPct(eng)}%;background:${threatColor(eng)};box-shadow:0 0 8px ${threatColor(eng)}80`"></div>
          </div>
        </div>

        <!-- Severity indicators -->
        <div class="grid grid-cols-4 gap-1.5 mb-3">
          <div class="text-center py-1.5 rounded-lg" :style="eng.stats.critical ? 'background:rgba(255,56,100,0.08);border:1px solid rgba(255,56,100,0.15)' : 'background:rgba(0,0,0,0.2);border:1px solid #1e2d3d'">
            <div class="text-sm font-bold" :style="eng.stats.critical ? 'color:#ff3864' : 'color:#2d4356'" style="font-family:'Rajdhani',sans-serif;">{{ eng.stats.critical || 0 }}</div>
            <div class="text-[9px] uppercase" :style="eng.stats.critical ? 'color:#ff386490' : 'color:#2d4356'" style="font-family:'Rajdhani',sans-serif;letter-spacing:0.1em;">Crit</div>
          </div>
          <div class="text-center py-1.5 rounded-lg" :style="eng.stats.high ? 'background:rgba(255,107,53,0.08);border:1px solid rgba(255,107,53,0.15)' : 'background:rgba(0,0,0,0.2);border:1px solid #1e2d3d'">
            <div class="text-sm font-bold" :style="eng.stats.high ? 'color:#ff6b35' : 'color:#2d4356'" style="font-family:'Rajdhani',sans-serif;">{{ eng.stats.high || 0 }}</div>
            <div class="text-[9px] uppercase" :style="eng.stats.high ? 'color:#ff6b3590' : 'color:#2d4356'" style="font-family:'Rajdhani',sans-serif;letter-spacing:0.1em;">Alta</div>
          </div>
          <div class="text-center py-1.5 rounded-lg" :style="eng.stats.medium ? 'background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.15)' : 'background:rgba(0,0,0,0.2);border:1px solid #1e2d3d'">
            <div class="text-sm font-bold" :style="eng.stats.medium ? 'color:#f59e0b' : 'color:#2d4356'" style="font-family:'Rajdhani',sans-serif;">{{ eng.stats.medium || 0 }}</div>
            <div class="text-[9px] uppercase" :style="eng.stats.medium ? 'color:#f59e0b90' : 'color:#2d4356'" style="font-family:'Rajdhani',sans-serif;letter-spacing:0.1em;">Med</div>
          </div>
          <div class="text-center py-1.5 rounded-lg" style="background:rgba(0,0,0,0.2);border:1px solid #1e2d3d;">
            <div class="text-sm font-bold text-cyan" style="font-family:'Rajdhani',sans-serif;">{{ eng.stats.hosts }}</div>
            <div class="text-[9px] uppercase" style="color:#4b6277;font-family:'Rajdhani',sans-serif;letter-spacing:0.1em;">Hosts</div>
          </div>
        </div>

        <div class="flex items-center justify-between">
          <span class="text-xs" style="color:#4b6277;font-family:'JetBrains Mono',monospace;">{{ eng.start_date ? formatDate(eng.start_date) : 'Sin fecha' }}</span>
          <span class="text-xs font-bold uppercase tracking-wider transition-colors group-hover:text-cyan" style="color:#4b6277;font-family:'Rajdhani',sans-serif;letter-spacing:0.08em;">ABRIR →</span>
        </div>
        </RouterLink>
      </div>
    </div>

    <div v-else-if="!loading" class="flex flex-col items-center justify-center py-20">
      <div class="text-6xl mb-4 opacity-20">🎯</div>
      <div class="text-base font-bold mb-1" style="color:#4b6277;font-family:'Rajdhani',sans-serif;">Sin engagements</div>
      <div class="text-sm mb-6" style="color:#2d4356;">Crea tu primer proyecto de auditoría</div>
      <button @click="showModal = true" class="btn-primary">+ Nuevo Engagement</button>
    </div>

    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <div v-for="i in 6" :key="i" class="h-44 rounded-xl animate-pulse" style="background:#0d1117;border:1px solid #1e2d3d;"></div>
    </div>

    <!-- Modal -->
    <Teleport to="body">
      <Transition name="v">
        <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="showModal = false"></div>
          <div class="relative w-full max-w-lg shadow-panel rounded-2xl" style="background:linear-gradient(135deg,#0d1117,#111827);border:1px solid #1e2d3d;">
            <!-- Modal header -->
            <div class="flex items-center justify-between px-6 py-4 border-b" style="border-color:#1e2d3d;">
              <div class="flex items-center gap-2">
                <div class="w-1 h-5 rounded-full bg-cyan"></div>
                <span class="font-bold" style="font-family:'Rajdhani',sans-serif;letter-spacing:0.06em;color:#fff;font-size:15px;">NUEVO ENGAGEMENT</span>
              </div>
              <button @click="showModal = false" style="color:#4b6277;">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>
            <form @submit.prevent="createEngagement" class="p-6 space-y-4">
              <div>
                <label class="block mb-1.5 text-xs uppercase tracking-wider" style="color:#4b6277;font-family:'Rajdhani',sans-serif;font-weight:700;">Cliente *</label>
                <input v-model="form.client" required class="input" placeholder="Acme Corp S.L." />
              </div>
              <div>
                <label class="block mb-1.5 text-xs uppercase tracking-wider" style="color:#4b6277;font-family:'Rajdhani',sans-serif;font-weight:700;">Nombre del Proyecto *</label>
                <input v-model="form.name" required class="input" placeholder="Auditoría Red Interna Q2 2026" />
              </div>
              <div>
                <label class="block mb-1.5 text-xs uppercase tracking-wider" style="color:#4b6277;font-family:'Rajdhani',sans-serif;font-weight:700;">Descripción</label>
                <textarea v-model="form.description" class="input h-20 resize-none" placeholder="Alcance, objetivos, restricciones..."></textarea>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block mb-1.5 text-xs uppercase tracking-wider" style="color:#4b6277;font-family:'Rajdhani',sans-serif;font-weight:700;">Fecha Inicio</label>
                  <input v-model="form.start_date" type="date" class="input" />
                </div>
                <div>
                  <label class="block mb-1.5 text-xs uppercase tracking-wider" style="color:#4b6277;font-family:'Rajdhani',sans-serif;font-weight:700;">Fecha Fin</label>
                  <input v-model="form.end_date" type="date" class="input" />
                </div>
              </div>
              <div class="flex gap-3 pt-2">
                <button type="button" @click="showModal = false" class="btn-ghost flex-1 justify-center">Cancelar</button>
                <button type="submit" :disabled="saving" class="btn-primary flex-1 justify-center">
                  {{ saving ? 'Creando...' : 'CREAR ENGAGEMENT' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/composables/api'
import StatusBadge from '@/components/StatusBadge.vue'

const router       = useRouter()
const engagements  = ref([])
const loading      = ref(true)
const showModal    = ref(false)
const saving       = ref(false)
const search       = ref('')
const statusFilter = ref('')
const form = ref({ client: '', name: '', description: '', start_date: '', end_date: '' })

const STATUS_OPTS = [
  { value: 'planning',  label: 'Planificación' },
  { value: 'active',    label: 'Activo' },
  { value: 'paused',    label: 'Pausado' },
  { value: 'completed', label: 'Completado' },
  { value: 'archived',  label: 'Archivado' },
]

const filtered = computed(() => {
  let list = engagements.value
  if (statusFilter.value) list = list.filter(e => e.status === statusFilter.value)
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(e => e.client.toLowerCase().includes(q) || e.name.toLowerCase().includes(q))
  }
  return list
})

function threatPct(eng) {
  const s = eng.stats
  return Math.min(100, (s.critical * 25 + s.high * 10 + s.medium * 3 + s.low * 1))
}
function threatColor(eng) {
  const p = threatPct(eng)
  if (p >= 75) return '#ff3864'
  if (p >= 40) return '#ff6b35'
  if (p >= 15) return '#f59e0b'
  return '#00ff9d'
}
function threatLabel(eng) {
  const p = threatPct(eng)
  if (p >= 75) return 'CRÍTICO'
  if (p >= 40) return 'ALTO'
  if (p >= 15) return 'MEDIO'
  if (p > 0)   return 'BAJO'
  return 'LIMPIO'
}
function formatDate(d) {
  return new Date(d).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' })
}

onMounted(async () => {
  try {
    const res = await api.get('/engagements/')
    engagements.value = res.data.results || res.data
  } finally { loading.value = false }
})

async function deleteEngagement(eng) {
  if (!confirm(`¿Eliminar "${eng.name}"?\nSe borrarán todos los hosts, vulnerabilidades y escaneos asociados. Esta acción no se puede deshacer.`)) return
  try {
    await api.delete(`/engagements/${eng.id}/`)
    engagements.value = engagements.value.filter(e => e.id !== eng.id)
  } catch (e) {
    alert('Error al eliminar: ' + (e.response?.data?.detail || e.message))
  }
}

async function createEngagement() {
  saving.value = true
  try {
    const res = await api.post('/engagements/', form.value)
    showModal.value = false
    router.push(`/engagements/${res.data.id}`)
  } catch (e) {
    alert('Error: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data)))
  } finally { saving.value = false }
}
</script>
