<template>
  <div class="space-y-4 animate-entry" style="height:100%;">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="page-title">Mapa de Red</h1>
        <p v-if="engName" class="page-subtitle">{{ engName }}</p>
      </div>
      <div class="flex items-center gap-4">
        <!-- Legend -->
        <div class="flex items-center gap-3 text-xs" style="color:#4b6277;font-family:'Rajdhani',sans-serif;letter-spacing:0.06em;">
          <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full inline-block" style="background:#ff3864;box-shadow:0 0 6px #ff386480;"></span>CRÍTICO</span>
          <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full inline-block" style="background:#ff6b35;box-shadow:0 0 6px #ff6b3580;"></span>ALTO</span>
          <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full inline-block" style="background:#f59e0b;box-shadow:0 0 6px #f59e0b80;"></span>MEDIO</span>
          <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full inline-block" style="background:#00d4ff;box-shadow:0 0 6px #00d4ff80;"></span>LIMPIO</span>
        </div>
        <!-- Node count -->
        <div class="px-3 py-1.5 rounded-xl text-xs font-bold" style="background:rgba(0,212,255,0.06);border:1px solid rgba(0,212,255,0.15);color:#4b6277;font-family:'Rajdhani',sans-serif;">
          {{ nodeCount }} NODOS
        </div>
      </div>
    </div>

    <!-- Map container -->
    <div class="card p-0 overflow-hidden relative" style="height:calc(100vh - 220px);">
      <!-- Subtle grid overlay -->
      <div style="position:absolute;inset:0;background-image:linear-gradient(rgba(0,212,255,0.02) 1px,transparent 1px),linear-gradient(90deg,rgba(0,212,255,0.02) 1px,transparent 1px);background-size:40px 40px;pointer-events:none;z-index:1;"></div>

      <div ref="networkContainer" style="width:100%;height:100%;position:relative;z-index:0;"></div>

      <!-- Loading overlay -->
      <div v-if="loading" style="position:absolute;inset:0;background:rgba(6,9,16,0.9);display:flex;align-items:center;justify-content:center;z-index:10;">
        <div class="text-center">
          <svg class="w-8 h-8 animate-spin text-cyan mx-auto mb-3" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
          <div class="text-sm font-bold text-cyan" style="font-family:'Rajdhani',sans-serif;">MAPEANDO RED...</div>
        </div>
      </div>

      <!-- Node detail panel -->
      <transition name="slide-panel">
        <div v-if="selected" class="absolute top-4 right-4 w-72" style="z-index:20;">
          <div class="card border-glow-cyan" style="background:rgba(6,9,16,0.95);">
            <div class="flex items-center justify-between mb-3">
              <div class="text-xs font-bold uppercase" style="color:#4b6277;font-family:'Rajdhani',sans-serif;letter-spacing:0.1em;">HOST SELECCIONADO</div>
              <button @click="selected = null" style="color:#4b6277;hover:color:#fff;">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>

            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center text-xl" style="background:rgba(0,212,255,0.08);border:1px solid rgba(0,212,255,0.2);">
                {{ OS_EMOJI[selected.os] || '🖥' }}
              </div>
              <div>
                <div class="font-mono text-cyan font-bold">{{ selected.ip }}</div>
                <div class="text-xs mt-0.5" style="color:#4b6277;">{{ selected.label !== selected.ip ? selected.label : selected.os || 'Unknown OS' }}</div>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-2 mb-4">
              <div class="px-3 py-2 rounded-lg text-xs" style="background:rgba(0,0,0,0.4);border:1px solid #1e2d3d;">
                <div style="color:#4b6277;font-family:'Rajdhani',sans-serif;letter-spacing:0.08em;text-transform:uppercase;">Puertos</div>
                <div class="text-cyan font-bold font-mono text-lg mt-0.5">{{ selected.ports }}</div>
              </div>
              <div class="px-3 py-2 rounded-lg text-xs" style="background:rgba(0,0,0,0.4);border:1px solid #1e2d3d;">
                <div style="color:#4b6277;font-family:'Rajdhani',sans-serif;letter-spacing:0.08em;text-transform:uppercase;">Risk Score</div>
                <div class="font-bold font-mono text-lg mt-0.5"
                  :style="`color:${(selected.risk||0) > 70 ? '#ff3864' : (selected.risk||0) > 40 ? '#ff6b35' : '#00ff9d'}`">
                  {{ (selected.risk || 0).toFixed(0) }}
                </div>
              </div>
            </div>

            <div class="mb-4">
              <div class="flex justify-between text-xs mb-1">
                <span style="color:#4b6277;font-family:'Rajdhani',sans-serif;">SEVERIDAD MÁX.</span>
                <span :class="`badge-${selected.severity}`">{{ selected.severity || 'none' }}</span>
              </div>
              <div class="h-1 rounded-full overflow-hidden" style="background:#1e2d3d;">
                <div class="h-full rounded-full" :style="`width:${Math.min(selected.risk||0,100)}%;background:${(selected.risk||0) > 70 ? '#ff3864' : (selected.risk||0) > 40 ? '#ff6b35' : '#00ff9d'};transition:width 0.5s;`"></div>
              </div>
            </div>

            <RouterLink :to="`/hosts/${selected.id}`" class="btn-primary w-full text-center text-xs block">
              VER DETALLE COMPLETO →
            </RouterLink>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Network } from 'vis-network/standalone'
import api from '@/composables/api'

const route = useRoute()
const id    = route.params.id

const networkContainer = ref(null)
const selected  = ref(null)
const loading   = ref(true)
const nodeCount = ref(0)
const engName   = ref('')

const OS_EMOJI = { windows: '🪟', linux: '🐧', macos: '🍎', network: '🌐', embedded: '📟', unknown: '🖥' }

const SEV_COLORS = {
  critical: { background: '#ff3864', border: '#ff3864', highlight: { background: '#ff6090', border: '#ff3864' } },
  high:     { background: '#ff6b35', border: '#ff6b35', highlight: { background: '#ff8c5f', border: '#ff6b35' } },
  medium:   { background: '#f59e0b', border: '#f59e0b', highlight: { background: '#fbbf24', border: '#f59e0b' } },
  low:      { background: '#4cc9f0', border: '#4cc9f0', highlight: { background: '#7dd9f5', border: '#4cc9f0' } },
  info:     { background: '#1e2d3d', border: '#00d4ff', highlight: { background: '#2d4356', border: '#00d4ff' } },
}

const OS_SHAPES = {
  windows: 'square', linux: 'diamond', network: 'triangle',
  macos: 'dot', embedded: 'star', unknown: 'dot',
}

onMounted(async () => {
  try {
    // Load engagement name
    const engRes = await api.get(`/engagements/${id}/`)
    engName.value = engRes.data.name || ''

    const res = await api.get(`/engagements/${id}/network_map/`)
    const { nodes: rawNodes } = res.data

    nodeCount.value = rawNodes.length

    const nodes = rawNodes.map(n => ({
      id:    n.id,
      label: n.label || n.ip,
      title: `${n.ip} — ${n.os || 'Unknown OS'}\n${n.ports} ports open | Risk: ${(n.risk || 0).toFixed(0)}`,
      color: SEV_COLORS[n.severity] || SEV_COLORS.info,
      shape: OS_SHAPES[n.os] || 'dot',
      size:  Math.max(16, Math.min(42, 16 + (n.risk || 0) / 4)),
      font:  {
        color: '#c9d8e5',
        size:  11,
        face:  'JetBrains Mono, monospace',
        bold:  { color: '#00d4ff' },
      },
      shadow: { enabled: true, color: `${(SEV_COLORS[n.severity] || SEV_COLORS.info).border}80`, size: 12 },
      ...n,
    }))

    // Edges: connect nodes in same /24 subnet
    const edges = []
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i].ip?.split('.').slice(0, 3).join('.')
        const b = nodes[j].ip?.split('.').slice(0, 3).join('.')
        if (a && b && a === b) {
          edges.push({
            from:  nodes[i].id,
            to:    nodes[j].id,
            color: { color: '#1e2d3d', opacity: 0.6, highlight: '#00d4ff40' },
            width: 1,
            smooth: { type: 'curvedCW', roundness: 0.1 },
          })
        }
      }
    }

    const network = new Network(
      networkContainer.value,
      { nodes, edges },
      {
        physics: {
          solver: 'forceAtlas2Based',
          forceAtlas2Based: { gravitationalConstant: -60, centralGravity: 0.01, springLength: 120, springConstant: 0.08, damping: 0.4 },
          stabilization: { iterations: 250, fit: true },
        },
        interaction: {
          hover: true,
          tooltipDelay: 200,
          navigationButtons: false,
          keyboard: { enabled: true },
          zoomView: true,
          dragView: true,
        },
        nodes: {
          borderWidth: 2,
          borderWidthSelected: 3,
        },
        edges: {
          smooth: { type: 'continuous' },
          arrows: { to: { enabled: false } },
        },
        layout: { randomSeed: 42 },
      }
    )

    network.on('click', params => {
      if (params.nodes.length > 0) {
        const node = nodes.find(n => n.id === params.nodes[0])
        selected.value = node || null
      } else {
        selected.value = null
      }
    })

    network.on('stabilizationIterationsDone', () => {
      loading.value = false
      network.fit({ animation: { duration: 800, easingFunction: 'easeInOutQuad' } })
    })

  } catch (e) {
    loading.value = false
    console.error('NetworkMap error:', e)
  }
})
</script>

<style scoped>
.slide-panel-enter-active, .slide-panel-leave-active { transition: all 0.25s ease; }
.slide-panel-enter-from, .slide-panel-leave-to { opacity: 0; transform: translateX(20px); }
</style>
