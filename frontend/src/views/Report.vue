<template>
  <div class="space-y-5 animate-entry">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="page-title">Informe de Auditoría</h1>
        <p v-if="eng" class="page-subtitle">{{ eng.client }} — {{ eng.name }}</p>
      </div>
      <div class="flex gap-3">
        <button @click="generateReport" :disabled="generating" class="btn-primary">
          <svg v-if="generating" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
          <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
          {{ generating ? 'GENERANDO...' : 'GENERAR PDF' }}
        </button>
        <a v-if="pdfReady" :href="`/api/reports/${id}/download/`" target="_blank" class="btn-ghost">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
          DESCARGAR
        </a>
      </div>
    </div>

    <!-- Progress -->
    <div v-if="generating" class="card border-glow-cyan" style="background:rgba(0,212,255,0.03);">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl flex items-center justify-center glow-cyan" style="background:rgba(0,212,255,0.1);border:1px solid rgba(0,212,255,0.2);">
          <svg class="w-6 h-6 animate-spin text-cyan" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
        </div>
        <div>
          <div class="text-sm font-bold text-cyan" style="font-family:'Rajdhani',sans-serif;letter-spacing:0.04em;">GENERANDO INFORME CON CLAUDE AI</div>
          <div class="text-xs mt-1" style="color:#4b6277;">Redactando executive summary, metodología y conclusiones...</div>
          <div class="mt-2 h-1 rounded-full overflow-hidden" style="background:#1e2d3d;width:300px;">
            <div class="h-full animate-shimmer rounded-full" style="background:linear-gradient(90deg,rgba(0,212,255,0.2),rgba(0,212,255,0.8),rgba(0,212,255,0.2));background-size:200% 100%;width:75%;"></div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="pdfReady && !generating" class="flex items-center gap-3 px-4 py-3 rounded-xl" style="background:rgba(0,255,157,0.06);border:1px solid rgba(0,255,157,0.2);">
      <span class="text-green text-xl">✅</span>
      <div>
        <div class="text-sm font-bold text-green" style="font-family:'Rajdhani',sans-serif;">INFORME GENERADO CORRECTAMENTE</div>
        <div class="text-xs mt-0.5" style="color:#4b6277;">PDF profesional listo para entregar al cliente</div>
      </div>
    </div>

    <!-- Content -->
    <div v-if="eng" class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div class="space-y-4">
        <!-- Client info -->
        <div class="card">
          <div class="flex items-center gap-2 mb-4"><div class="w-1 h-5 rounded-full bg-cyan"></div><span class="section-title">Cliente</span></div>
          <div class="space-y-3">
            <div>
              <div class="text-xs" style="color:#4b6277;font-family:'Rajdhani',sans-serif;letter-spacing:0.1em;text-transform:uppercase;">Empresa</div>
              <div class="text-sm font-bold mt-0.5" style="color:#fff;font-family:'Rajdhani',sans-serif;">{{ eng.client }}</div>
            </div>
            <div>
              <div class="text-xs" style="color:#4b6277;font-family:'Rajdhani',sans-serif;letter-spacing:0.1em;text-transform:uppercase;">Proyecto</div>
              <div class="text-sm mt-0.5" style="color:#c9d8e5;">{{ eng.name }}</div>
            </div>
            <div class="flex items-center justify-between">
              <div class="text-xs" style="color:#4b6277;font-family:'Rajdhani',sans-serif;letter-spacing:0.1em;text-transform:uppercase;">Estado</div>
              <StatusBadge :status="eng.status" />
            </div>
            <div v-if="eng.start_date" class="flex items-center justify-between">
              <div class="text-xs" style="color:#4b6277;font-family:'Rajdhani',sans-serif;letter-spacing:0.1em;text-transform:uppercase;">Período</div>
              <div class="text-xs font-mono" style="color:#4b6277;">{{ eng.start_date }} → {{ eng.end_date || '—' }}</div>
            </div>
          </div>
        </div>

        <!-- Findings -->
        <div class="card">
          <div class="flex items-center gap-2 mb-4"><div class="w-1 h-5 rounded-full bg-red"></div><span class="section-title">Hallazgos</span></div>
          <div class="space-y-2">
            <div v-for="item in findings" :key="item.label" class="flex items-center gap-3 p-2 rounded-lg"
              :style="item.count > 0 ? `background:${item.bg};border:1px solid ${item.border};` : 'background:rgba(0,0,0,0.2);border:1px solid #1e2d3d;'">
              <div class="w-2 h-2 rounded-full flex-shrink-0" :style="`background:${item.color}`"></div>
              <div class="flex-1 text-sm" :style="`color:${item.count > 0 ? item.color : '#4b6277'};font-family:'Rajdhani',sans-serif;font-weight:700;letter-spacing:0.04em;`">{{ item.label }}</div>
              <div class="text-lg font-bold" :style="`color:${item.count > 0 ? item.color : '#2d4356'};font-family:'Rajdhani',sans-serif;`">{{ item.count }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: scope + AI narrative -->
      <div class="lg:col-span-2 space-y-4">
        <div v-if="eng.targets?.length" class="card">
          <div class="flex items-center gap-2 mb-4"><div class="w-1 h-5 rounded-full bg-cyan"></div><span class="section-title">Alcance del Engagement</span></div>
          <div class="space-y-2">
            <div v-for="t in eng.targets" :key="t.id" class="flex items-center justify-between p-2.5 rounded-lg" style="background:rgba(0,0,0,0.3);border:1px solid #1e2d3d;">
              <span class="font-mono text-sm text-cyan">{{ t.value }}</span>
              <div class="flex items-center gap-2">
                <span v-if="t.description" class="text-xs" style="color:#4b6277;">{{ t.description }}</span>
                <span :class="t.in_scope ? 'text-green' : 'text-muted'" class="text-xs font-bold" style="font-family:'Rajdhani',sans-serif;">{{ t.in_scope ? '● IN SCOPE' : '○ OUT' }}</span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="eng.notes" class="card border-glow-cyan" style="background:rgba(0,212,255,0.03);">
          <div class="flex items-center gap-2 mb-3">
            <span class="text-cyan text-sm font-bold" style="font-family:'Rajdhani',sans-serif;letter-spacing:0.06em;">🤖 NARRATIVA GENERADA POR CLAUDE AI</span>
          </div>
          <div class="text-sm leading-relaxed whitespace-pre-wrap" style="color:#8ba5bc;">{{ eng.notes }}</div>
        </div>

        <div v-else class="card border-glow-cyan" style="background:rgba(0,212,255,0.02);">
          <div class="flex items-center gap-3">
            <div class="text-3xl opacity-40">🤖</div>
            <div>
              <div class="text-sm font-bold" style="color:#4b6277;font-family:'Rajdhani',sans-serif;">ANÁLISIS AI PENDIENTE</div>
              <div class="text-xs mt-0.5" style="color:#2d4356;">Genera el PDF para activar la narrativa automática con Claude Sonnet</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/composables/api'
import StatusBadge from '@/components/StatusBadge.vue'

const route      = useRoute()
const id         = route.params.id
const eng        = ref(null)
const generating = ref(false)
const pdfReady   = ref(false)

const findings = computed(() => {
  if (!eng.value?.stats) return []
  const s = eng.value.stats
  return [
    { label: 'CRÍTICA', count: s.critical, color: '#ff3864', bg: 'rgba(255,56,100,0.08)', border: 'rgba(255,56,100,0.15)' },
    { label: 'ALTA',    count: s.high,     color: '#ff6b35', bg: 'rgba(255,107,53,0.08)', border: 'rgba(255,107,53,0.15)' },
    { label: 'MEDIA',   count: s.medium,   color: '#f59e0b', bg: 'rgba(245,158,11,0.08)', border: 'rgba(245,158,11,0.15)' },
    { label: 'BAJA',    count: s.low,      color: '#4cc9f0', bg: 'rgba(76,201,240,0.08)', border: 'rgba(76,201,240,0.15)' },
    { label: 'INFO',    count: s.info,     color: '#4b6277', bg: 'transparent',           border: '#1e2d3d' },
  ]
})

onMounted(async () => {
  const res = await api.get(`/engagements/${id}/`)
  eng.value = res.data
})

async function generateReport() {
  generating.value = true
  pdfReady.value   = false
  try {
    await api.post(`/reports/${id}/generate/`)
    pdfReady.value = true
    const res = await api.get(`/engagements/${id}/`)
    eng.value = res.data
  } catch (e) {
    alert('Error generando informe: ' + (e.response?.data?.detail || e.message))
  } finally { generating.value = false }
}
</script>
