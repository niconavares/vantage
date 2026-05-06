<template>
  <div class="space-y-5 animate-entry">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="page-title">Scan Jobs</h1>
        <p class="page-subtitle">Historial y logs de operaciones de escaneo</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg" style="background:rgba(0,0,0,0.4);border:1px solid #1e2d3d;">
          <span class="w-2 h-2 rounded-full transition-all" :class="wsConnected ? 'bg-green animate-pulse' : 'bg-muted'"></span>
          <span class="text-xs font-bold uppercase tracking-wider"
            :style="wsConnected ? 'color:#00ff9d;font-family:Rajdhani,sans-serif;' : 'color:#4b6277;font-family:Rajdhani,sans-serif;'">
            {{ wsConnected ? 'LIVE' : 'OFFLINE' }}
          </span>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-5 gap-4">

      <!-- Job list panel -->
      <div class="lg:col-span-2 space-y-2">
        <div class="section-title px-1 mb-3">Operaciones Recientes</div>

        <div v-if="loading" class="space-y-2">
          <div v-for="i in 5" :key="i" class="h-16 rounded-xl animate-pulse" style="background:#0d1117;border:1px solid #1e2d3d;"></div>
        </div>

        <div v-for="job in jobs" :key="job.id"
          class="p-3 rounded-xl border transition-all cursor-pointer group relative"
          :style="selectedJob?.id === job.id
            ? 'border-color:rgba(0,212,255,0.35);background:rgba(0,212,255,0.05);box-shadow:0 0 15px rgba(0,212,255,0.06);'
            : 'border-color:#1e2d3d;background:rgba(0,0,0,0.3);'"
          @click="selectJob(job)">
          <div class="flex items-center gap-3">
            <!-- Status icon -->
            <div class="w-9 h-9 rounded-lg flex items-center justify-center text-base flex-shrink-0 relative"
              :style="`background:${jobColor(job.status).bg};border:1px solid ${jobColor(job.status).border};`">
              {{ jobIcon(job.status) }}
              <span v-if="job.status === 1" class="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-cyan animate-pulse"></span>
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-sm font-bold truncate" style="color:#c9d8e5;font-family:'Rajdhani',sans-serif;letter-spacing:0.03em;">{{ SCAN_LABELS[job.scan_type] || job.scan_type }}</div>
              <div class="text-xs truncate" style="color:#4b6277;font-family:'JetBrains Mono',monospace;">{{ targetsArr(job.targets).join(', ') }}</div>
            </div>
            <div class="text-right flex-shrink-0 flex items-center gap-2">
              <div>
                <div class="text-[10px]" style="color:#4b6277;">{{ formatDate(job.created_at) }}</div>
                <div class="flex items-center gap-1.5 mt-0.5 justify-end">
                  <span v-if="job.hosts_found" class="text-[10px] font-mono" style="color:#00d4ff;">{{ job.hosts_found }}h</span>
                  <span v-if="job.vulns_found" class="text-[10px] font-mono" style="color:#ff6b35;">{{ job.vulns_found }}v</span>
                </div>
              </div>
              <!-- Delete button — always visible, never for running jobs -->
              <button v-if="job.status !== 1"
                @click.stop="confirmDelete(job)"
                class="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 transition-all hover:scale-110"
                style="color:#ff3864;background:rgba(255,56,100,0.12);border:1px solid rgba(255,56,100,0.25);"
                title="Eliminar escaneo">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <div v-if="!loading && !jobs.length" class="text-center py-12" style="color:#4b6277;">
          <div class="text-3xl mb-2 opacity-40">📡</div>
          <div class="text-sm">Sin operaciones registradas</div>
        </div>
      </div>

      <!-- Terminal log panel -->
      <div class="lg:col-span-3">
        <div v-if="selectedJob" class="flex flex-col" style="min-height:520px;">

          <!-- Job header + progress -->
          <div class="card mb-3 flex-shrink-0">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl flex items-center justify-center text-lg"
                  :style="`background:${jobColor(selectedJob.status).bg};border:1px solid ${jobColor(selectedJob.status).border};`">
                  {{ jobIcon(selectedJob.status) }}
                </div>
                <div>
                  <div class="text-base font-bold" style="color:#fff;font-family:'Rajdhani',sans-serif;letter-spacing:0.04em;">{{ SCAN_LABELS[selectedJob.scan_type] }}</div>
                  <div class="text-xs font-mono" style="color:#4b6277;">{{ selectedJob.id }}</div>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <div class="text-right">
                  <div class="text-xs font-mono" style="color:#4b6277;">{{ targetsArr(selectedJob.targets).join(', ') }}</div>
                  <div class="flex items-center gap-2 mt-1 justify-end">
                    <span class="text-xs font-mono" style="color:#00d4ff;">{{ selectedJob.hosts_found }} hosts</span>
                    <span class="text-xs font-mono" style="color:#ff6b35;">{{ selectedJob.vulns_found }} vulns</span>
                  </div>
                </div>
                <span class="px-2 py-1 rounded-lg text-xs font-bold uppercase"
                  :style="`background:${jobColor(selectedJob.status).bg};border:1px solid ${jobColor(selectedJob.status).border};color:${jobColor(selectedJob.status).text};font-family:'Rajdhani',sans-serif;letter-spacing:0.08em;`">
                  {{ jobLabel(selectedJob.status) }}
                </span>
              </div>
            </div>

            <!-- Progress bar — only for running jobs -->
            <div v-if="selectedJob.status === 1" class="mt-4">
              <div class="flex items-center justify-between mb-1.5">
                <span class="text-xs font-bold uppercase tracking-wider" style="color:#4b6277;font-family:'Rajdhani',sans-serif;">
                  {{ currentPhaseLabel }}
                </span>
                <span class="text-sm font-bold font-mono" style="color:#00d4ff;">{{ progress.toFixed(2) }}%</span>
              </div>
              <div class="h-2 rounded-full overflow-hidden" style="background:#0d1117;border:1px solid #1e2d3d;">
                <div class="h-full rounded-full transition-all duration-1000"
                  :style="`width:${progress}%;background:linear-gradient(90deg,#00d4ff,#00ff9d);box-shadow:0 0 8px rgba(0,212,255,0.5);`"></div>
              </div>
              <div class="flex justify-between mt-1">
                <span v-for="(ph, i) in PHASE_MILESTONES" :key="i"
                  class="text-[9px] uppercase"
                  :style="`color:${progress >= ph.pct ? '#00d4ff' : '#2d4356'};font-family:'Rajdhani',sans-serif;`">
                  {{ ph.short }}
                </span>
              </div>
            </div>

            <!-- Completed / failed summary -->
            <div v-else-if="selectedJob.status === 2" class="mt-3 flex items-center gap-3 px-3 py-2 rounded-lg" style="background:rgba(0,255,157,0.05);border:1px solid rgba(0,255,157,0.15);">
              <span class="text-green text-sm">✅</span>
              <span class="text-xs" style="color:#00ff9d;font-family:'Rajdhani',sans-serif;">Completado sin errores — {{ selectedJob.ports_found || 0 }} puertos · {{ selectedJob.vulns_found || 0 }} vulns</span>
            </div>
            <div v-else-if="selectedJob.status === 0" class="mt-3 px-3 py-2 rounded-lg" style="background:rgba(255,56,100,0.05);border:1px solid rgba(255,56,100,0.15);">
              <span class="text-xs" style="color:#ff3864;font-family:'JetBrains Mono',monospace;">{{ selectedJob.error_msg || 'Error desconocido' }}</span>
            </div>
          </div>

          <!-- Terminal -->
          <div class="terminal flex-1 overflow-y-auto" ref="logBox" style="min-height:400px;max-height:520px;">
            <div v-if="!logs.length" class="text-center py-16" style="color:#2d4356;">
              <div class="text-2xl mb-2">_</div>
              <div>Sin logs disponibles</div>
            </div>
            <div v-for="(log, idx) in logs" :key="idx" class="flex gap-3 mb-1">
              <span class="flex-shrink-0 select-none" style="color:#2d4356;font-size:11px;min-width:60px;">{{ formatTime(log.created_at || log.timestamp) }}</span>
              <span class="flex-shrink-0 w-14 text-right" :class="`log-${log.level}`" style="font-size:10px;opacity:0.7;letter-spacing:0.06em;text-transform:uppercase;">{{ log.level }}</span>
              <span :class="`log-${log.level}`" style="font-size:12px;line-height:1.5;word-break:break-all;">{{ log.message }}</span>
            </div>
            <!-- Blinking cursor when running -->
            <div v-if="selectedJob.status === 1" class="flex gap-2 mt-2 items-center">
              <span style="color:#2d4356;font-size:11px;min-width:60px;">{{ lastTime }}</span>
              <span class="animate-pulse" style="color:#00d4ff;font-size:14px;">▊</span>
            </div>
          </div>
        </div>

        <div v-else class="flex flex-col items-center justify-center rounded-xl border" style="min-height:520px;background:rgba(0,0,0,0.2);border-color:#1e2d3d;">
          <div class="text-5xl mb-4 opacity-20">🖥</div>
          <div class="text-sm" style="color:#4b6277;">Selecciona un job para ver los logs</div>
        </div>
      </div>
    </div>

    <!-- Delete confirmation modal -->
    <Teleport to="body">
      <Transition name="v">
        <div v-if="deleteTarget" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="deleteTarget = null"></div>
          <div class="relative w-full max-w-sm shadow-panel rounded-2xl p-6" style="background:linear-gradient(135deg,#0d1117,#111827);border:1px solid #1e2d3d;">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center" style="background:rgba(255,56,100,0.1);border:1px solid rgba(255,56,100,0.2);">
                <svg class="w-5 h-5" style="color:#ff3864;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </div>
              <div>
                <div class="font-bold" style="color:#fff;font-family:'Rajdhani',sans-serif;letter-spacing:0.04em;">Eliminar escaneo</div>
                <div class="text-xs mt-0.5" style="color:#4b6277;">Esta acción no se puede deshacer</div>
              </div>
            </div>
            <div class="px-3 py-2 rounded-lg mb-5" style="background:rgba(0,0,0,0.4);border:1px solid #1e2d3d;">
              <div class="text-sm font-bold" style="color:#8ba5bc;font-family:'Rajdhani',sans-serif;">{{ SCAN_LABELS[deleteTarget.scan_type] }}</div>
              <div class="text-xs font-mono mt-0.5" style="color:#4b6277;">{{ targetsArr(deleteTarget.targets).join(', ') }}</div>
            </div>
            <div class="flex gap-3">
              <button @click="deleteTarget = null" class="btn-ghost flex-1 justify-center">Cancelar</button>
              <button @click="executeDelete" :disabled="deleting" class="flex-1 justify-center flex items-center gap-2 px-4 py-2 rounded-xl font-bold text-sm uppercase tracking-wider transition-all"
                style="background:rgba(255,56,100,0.15);border:1px solid rgba(255,56,100,0.3);color:#ff3864;font-family:'Rajdhani',sans-serif;">
                {{ deleting ? 'Eliminando...' : 'ELIMINAR' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed, watch } from 'vue'
import api from '@/composables/api'
import { useAuthStore } from '@/stores/auth'

const auth         = useAuthStore()
const jobs         = ref([])
const loading      = ref(true)
const selectedJob  = ref(null)
const logs         = ref([])
const logBox       = ref(null)
const wsConnected  = ref(false)
const deleteTarget = ref(null)
const deleting     = ref(false)
let ws             = null
let progressTimer  = null

// ── Constants ─────────────────────────────────────────────────────────────────

const STATUS_ICONS  = { '-1': '🕐', '-1_n': '🕐', 1: '⚡', 2: '✅', 0: '❌', 3: '🚫' }
const STATUS_LABELS = { '-1': 'EN COLA', 1: 'RUNNING', 2: 'COMPLETO', 0: 'FALLIDO', 3: 'CANCELADO' }
const JOB_COLORS = {
  '-1': { bg: 'rgba(75,98,119,0.15)',  border: 'rgba(75,98,119,0.3)',  text: '#4b6277' },
  1:    { bg: 'rgba(0,212,255,0.1)',   border: 'rgba(0,212,255,0.25)', text: '#00d4ff' },
  2:    { bg: 'rgba(0,255,157,0.1)',   border: 'rgba(0,255,157,0.25)', text: '#00ff9d' },
  0:    { bg: 'rgba(255,56,100,0.1)',  border: 'rgba(255,56,100,0.25)',text: '#ff3864' },
  3:    { bg: 'rgba(245,158,11,0.1)',  border: 'rgba(245,158,11,0.25)',text: '#f59e0b' },
}

// Normalize targets to array regardless of API shape
function targetsArr(t) {
  if (!t) return []
  if (Array.isArray(t)) return t
  return String(t).split(',').map(s => s.trim()).filter(Boolean)
}
// Safe status key lookup (handles numeric -1 vs string '-1')
function jobIcon(status)  { return STATUS_ICONS[status]  ?? STATUS_ICONS[String(status)]  ?? '❓' }
function jobLabel(status) { return STATUS_LABELS[status] ?? STATUS_LABELS[String(status)] ?? String(status) }
function jobColor(status) { return JOB_COLORS[status]    ?? JOB_COLORS[String(status)]    ?? JOB_COLORS[3] }
const SCAN_LABELS = {
  discovery: 'Host Discovery', port: 'Port Scan', service: 'Service Detection',
  vuln: 'Vuln Scan (Nuclei)', ssl: 'SSL/TLS Audit', smb: 'SMB Audit', ad: 'AD Recon',
  brute: 'Brute Force', snmp: 'SNMP Audit', full: 'Full Audit',
}

// Phase milestones for full scan — each entry: { keyword, pct, label, short }
const PHASES = [
  { kw: 'Host discovery',       pct: 0,   end: 3,   label: 'Discovery',    short: 'DISC' },
  { kw: 'Port scan sobre',      pct: 3,   end: 55,  label: 'Port Scan',    short: 'PORTS' },
  { kw: 'SSL/TLS audit',        pct: 55,  end: 62,  label: 'SSL/TLS',      short: 'SSL' },
  { kw: 'SMB audit sobre',      pct: 62,  end: 68,  label: 'SMB',          short: 'SMB' },
  { kw: 'SNMP audit',           pct: 68,  end: 72,  label: 'SNMP',         short: 'SNMP' },
  { kw: 'Active Directory',     pct: 72,  end: 76,  label: 'AD Recon',     short: 'AD' },
  { kw: 'Credential audit',     pct: 76,  end: 82,  label: 'Brute Force',  short: 'BRUTE' },
  { kw: 'nuclei:',              pct: 82,  end: 99,  label: 'Nuclei',       short: 'NUCLEI' },
  { kw: 'Scan completado',      pct: 100, end: 100, label: 'Completado',   short: 'DONE' },
]
const PHASE_MILESTONES = PHASES.filter(p => p.short !== 'DISC').map(p => ({ pct: p.pct, short: p.short }))

// ── Progress tracking ─────────────────────────────────────────────────────────

const progress      = ref(0)   // real phase-based value
const displayProgress = ref(0) // slightly animated value shown to user
const currentPhaseLabel = ref('Iniciando...')
let phaseStartTime = null
let phaseStartPct  = 0
let phaseEndPct    = 3

// Estimated half-life per phase (seconds to reach ~50% of phase range)
const PHASE_DURATIONS = {
  'Iniciando...': 8,
  'Discovery':    30,
  'Port Scan':    600,   // half-fill after 10 min — still moves at 2hr
  'SSL/TLS':      60,
  'SMB':          30,
  'SNMP':         15,
  'AD Recon':     30,
  'Brute Force':  60,
  'Nuclei':       300,
  'Completado':   1,
}

function detectPhaseFromLogs() {
  // Find the HIGHEST phase index that appears in any log (walk newest first)
  const msgs = logs.value.map(l => l.message || '').reverse()
  for (const msg of msgs) {
    for (let i = PHASES.length - 1; i >= 0; i--) {
      if (msg.includes(PHASES[i].kw)) return PHASES[i]
    }
  }
  return PHASES[0]
}

function updateProgress() {
  if (!selectedJob.value || selectedJob.value.status !== 1) return

  const phase = detectPhaseFromLogs()

  // Phase transition — snap forward
  if (phase.label !== currentPhaseLabel.value) {
    currentPhaseLabel.value = phase.label
    phaseStartPct  = phase.pct
    phaseEndPct    = phase.end
    phaseStartTime = Date.now()
    if (phase.pct > progress.value) progress.value = phase.pct
  }

  if (phaseEndPct <= phaseStartPct) return

  const elapsed  = (Date.now() - (phaseStartTime || Date.now())) / 1000
  const range    = phaseEndPct - phaseStartPct
  const halfLife = PHASE_DURATIONS[phase.label] || 60

  // Hyperbolic curve: progress = range * t / (t + halfLife)
  // — at halfLife seconds → 50% of range
  // — never plateaus, always keeps incrementing (just slower)
  const fill   = range * elapsed / (elapsed + halfLife)
  const target = phaseStartPct + fill

  // Never go backwards; leave 0.02 gap from phaseEnd so the snap to next phase is visible
  if (target > progress.value) {
    progress.value = Math.min(target, phaseEndPct - 0.02)
  }

  // Animate display value: oscillate ±0.04 so decimals always show movement
  const t   = Date.now() / 1000
  const osc = 0.04 * Math.sin(t * 1.1) + 0.03 * Math.sin(t * 1.7)
  displayProgress.value = Math.min(
    Math.max(progress.value + osc, phaseStartPct),
    phaseEndPct - 0.01
  )
}

// ── WebSocket ──────────────────────────────────────────────────────────────────

let wsJobId       = null   // which job the WS is for
let wsReconnecting = false  // prevent multiple reconnect loops

function connectWs(jobId) {
  wsJobId = jobId
  wsReconnecting = false
  if (ws) { ws.close(); ws = null }

  const proto = location.protocol === 'https:' ? 'wss' : 'ws'
  try {
    ws = new WebSocket(`${proto}://${location.host}/ws/scan/${jobId}/?token=${auth.token}`)

    ws.onopen = () => {
      wsConnected.value = true
      wsReconnecting    = false
      // Consumer now sends full log history on connect — clear and reload to avoid dupes
      logs.value = []
    }

    ws.onclose = () => {
      wsConnected.value = false
      // Auto-reconnect if scan is still running and we haven't switched jobs
      if (wsJobId === jobId && selectedJob.value?.status === 1 && !wsReconnecting) {
        wsReconnecting = true
        setTimeout(() => {
          if (wsJobId === jobId && selectedJob.value?.status === 1) {
            connectWs(jobId)
          }
        }, 4000)
      }
    }

    ws.onerror = () => { ws && ws.close() }

    ws.onmessage = async (e) => {
      let data
      try { data = JSON.parse(e.data) } catch { return }

      if (data.type === 'log') {
        logs.value.push({
          level:      data.level      || 'info',
          message:    data.message    || '',
          created_at: data.timestamp  || new Date().toISOString(),
        })
        updateProgress()
        await nextTick()
        scrollToBottom()
      } else if (data.type === 'status') {
        const s = data.status
        if (selectedJob.value) selectedJob.value.status = s
        const idx = jobs.value.findIndex(j => j.id === jobId)
        if (idx >= 0) jobs.value[idx].status = s
        if (s === 2) {
          progress.value        = 100
          displayProgress.value = 100
          currentPhaseLabel.value = 'Completado'
        } else if (s === 0) {
          currentPhaseLabel.value = 'Error'
        }
      }
    }
  } catch {}
}

function scrollToBottom() {
  if (logBox.value) logBox.value.scrollTop = logBox.value.scrollHeight
}

// ── Job actions ───────────────────────────────────────────────────────────────

async function selectJob(job) {
  selectedJob.value = job
  logs.value = []
  progress.value = 0
  phaseStartTime = null
  currentPhaseLabel.value = 'Iniciando...'

  try {
    const res = await api.get(`/scan-jobs/${job.id}/`)
    logs.value = res.data.logs || []
    // Init progress from existing logs
    if (job.status === 1) {
      const phase = detectPhaseFromLogs()
      currentPhaseLabel.value = phase.label
      phaseStartPct  = phase.pct
      phaseEndPct    = phase.end
      phaseStartTime = Date.now()
      progress.value = phase.pct
    } else if (job.status === 2) {
      progress.value = 100
      currentPhaseLabel.value = 'Completado'
    }
  } catch {}

  connectWs(job.id)
  await nextTick()
  scrollToBottom()
}

function confirmDelete(job) {
  deleteTarget.value = job
}

async function executeDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await api.delete(`/scan-jobs/${deleteTarget.value.id}/`)
    jobs.value = jobs.value.filter(j => j.id !== deleteTarget.value.id)
    if (selectedJob.value?.id === deleteTarget.value.id) {
      selectedJob.value = null
      logs.value = []
    }
    deleteTarget.value = null
  } catch (e) {
    alert('Error al eliminar: ' + (e.response?.data?.detail || e.message))
  } finally {
    deleting.value = false
  }
}

// ── Computed ──────────────────────────────────────────────────────────────────

const lastTime = computed(() => {
  if (!logs.value.length) return ''
  const last = logs.value[logs.value.length - 1]
  return formatTime(last?.created_at || last?.timestamp)
})

// ── Polling ───────────────────────────────────────────────────────────────────

let pollInterval
async function pollJobs() {
  try {
    const res = await api.get('/scan-jobs/?page_size=50')
    jobs.value = res.data.results || res.data
    if (selectedJob.value) {
      const updated = jobs.value.find(j => j.id === selectedJob.value.id)
      if (updated) {
        selectedJob.value.hosts_found = updated.hosts_found
        selectedJob.value.vulns_found = updated.vulns_found
        selectedJob.value.ports_found = updated.ports_found
        if (selectedJob.value.status !== updated.status) {
          selectedJob.value.status = updated.status
          if (updated.status === 2) { progress.value = 100; currentPhaseLabel.value = 'Completado' }
        }
      }
    }
  } catch {}
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────

onMounted(async () => {
  try {
    const res = await api.get('/scan-jobs/?page_size=50')
    jobs.value = res.data.results || res.data
    const running = jobs.value.find(j => j.status === 1)
    if (running) selectJob(running)
  } finally {
    loading.value = false
  }
  pollInterval  = setInterval(pollJobs, 5000)
  progressTimer = setInterval(() => { if (selectedJob.value?.status === 1) updateProgress() }, 1000)
})

onUnmounted(() => {
  if (ws) ws.close()
  clearInterval(pollInterval)
  clearInterval(progressTimer)
})

// ── Formatters ────────────────────────────────────────────────────────────────

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
}
function formatTime(d) {
  if (!d) return ''
  try { return new Date(d).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) }
  catch { return '' }
}
</script>
