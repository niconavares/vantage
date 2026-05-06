<template>
  <div class="flex flex-col animate-entry" style="height:calc(100vh - 120px);max-width:900px;">

    <!-- Header -->
    <div class="flex items-center justify-between mb-5 flex-shrink-0">
      <div class="flex items-center gap-4">
        <div class="w-11 h-11 rounded-xl flex items-center justify-center glow-cyan" style="background:linear-gradient(135deg,rgba(0,212,255,0.15),rgba(0,212,255,0.05));border:1px solid rgba(0,212,255,0.25);">
          <svg class="w-5 h-5 text-cyan" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17H3a2 2 0 01-2-2V5a2 2 0 012-2h14a2 2 0 012 2v10a2 2 0 01-2 2h-2"/>
          </svg>
        </div>
        <div>
          <h1 class="page-title" style="font-size:24px;">AI Assistant</h1>
          <div class="flex items-center gap-2 mt-0.5">
            <span class="w-1.5 h-1.5 rounded-full bg-green animate-pulse"></span>
            <span class="text-xs uppercase tracking-wider" style="color:#4b6277;font-family:'Rajdhani',sans-serif;letter-spacing:0.12em;">Claude Sonnet · Online</span>
          </div>
        </div>
      </div>
      <button @click="clearChat" class="btn-ghost px-3 py-2 text-xs">
        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
        Limpiar
      </button>
    </div>

    <!-- Chat area -->
    <div ref="chatRef" class="flex-1 overflow-y-auto pr-1 space-y-4 mb-4" style="scrollbar-width:thin;">

      <!-- Welcome state -->
      <div v-if="!messages.length" class="flex flex-col items-center justify-center h-full py-12">
        <div class="w-20 h-20 rounded-2xl flex items-center justify-center mb-6 glow-cyan" style="background:linear-gradient(135deg,rgba(0,212,255,0.1),rgba(0,212,255,0.03));border:1px solid rgba(0,212,255,0.2);">
          <svg class="w-10 h-10 text-cyan" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
          </svg>
        </div>
        <h3 class="text-lg font-bold mb-1" style="font-family:'Rajdhani',sans-serif;color:#8ba5bc;letter-spacing:0.04em;">CLAUDE — Cyber Intelligence</h3>
        <p class="text-sm text-center mb-8 max-w-sm" style="color:#4b6277;">Pregunta sobre vulnerabilidades, técnicas de explotación, remediación o análisis de hallazgos.</p>

        <!-- Quick questions -->
        <div class="grid grid-cols-2 gap-2 w-full max-w-xl">
          <button v-for="q in QUICK_Q" :key="q.text" @click="sendQuestion(q.text)"
            class="flex items-start gap-3 p-3 rounded-xl text-left transition-all group"
            style="background:rgba(0,0,0,0.3);border:1px solid #1e2d3d;"
            onmouseover="this.style.borderColor='rgba(0,212,255,0.2)'"
            onmouseout="this.style.borderColor='#1e2d3d'">
            <span class="text-xl flex-shrink-0">{{ q.icon }}</span>
            <span class="text-xs group-hover:text-cyan transition-colors" style="color:#8ba5bc;line-height:1.5;">{{ q.text }}</span>
          </button>
        </div>
      </div>

      <!-- Messages -->
      <div v-for="msg in messages" :key="msg.id"
        class="flex gap-3" :class="msg.role === 'user' ? 'flex-row-reverse' : ''">

        <!-- Avatar -->
        <div class="w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center text-xs font-bold"
          :style="msg.role === 'user'
            ? 'background:rgba(0,212,255,0.12);border:1px solid rgba(0,212,255,0.2);color:#00d4ff;font-family:Rajdhani,sans-serif;'
            : 'background:rgba(0,0,0,0.4);border:1px solid #1e2d3d;color:#4b6277;'">
          {{ msg.role === 'user' ? (auth.user?.username?.slice(0,2).toUpperCase() || 'OP') : '🤖' }}
        </div>

        <!-- Bubble -->
        <div class="max-w-[78%] rounded-xl px-4 py-3 text-sm"
          :style="msg.role === 'user'
            ? 'background:rgba(0,212,255,0.08);border:1px solid rgba(0,212,255,0.15);color:#c9d8e5;'
            : 'background:rgba(0,0,0,0.4);border:1px solid #1e2d3d;color:#c9d8e5;'">
          <!-- Loading dots -->
          <div v-if="msg.loading" class="flex items-center gap-1.5 py-1">
            <span v-for="i in 3" :key="i" class="w-1.5 h-1.5 rounded-full bg-cyan animate-bounce"
              :style="`animation-delay:${(i-1)*150}ms`"></span>
          </div>
          <div v-else class="whitespace-pre-wrap leading-relaxed" style="font-size:13px;">{{ msg.content }}</div>
          <div class="text-[10px] mt-2 text-right" style="color:#4b6277;font-family:'JetBrains Mono',monospace;">{{ formatTime(msg.ts) }}</div>
        </div>
      </div>
    </div>

    <!-- Input -->
    <div class="flex-shrink-0">
      <div class="flex gap-3 p-3 rounded-xl" style="background:rgba(0,0,0,0.4);border:1px solid #1e2d3d;">
        <textarea v-model="input" @keydown.enter.exact.prevent="send"
          rows="1" class="flex-1 bg-transparent text-sm resize-none outline-none"
          style="color:#c9d8e5;font-family:'Inter',sans-serif;line-height:1.5;min-height:24px;max-height:120px;"
          placeholder="Pregunta sobre la auditoría... (Enter para enviar)"></textarea>
        <button @click="send" :disabled="!input.trim() || loading"
          class="btn-primary px-4 flex-shrink-0 self-end" style="height:36px;">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
          </svg>
        </button>
      </div>
      <p class="text-[10px] text-center mt-2" style="color:#2d4356;font-family:'Rajdhani',sans-serif;letter-spacing:0.08em;">
        CLAUDE SONNET · Modelo de análisis de ciberseguridad
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import api from '@/composables/api'
import { useAuthStore } from '@/stores/auth'

const auth     = useAuthStore()
const messages = ref([])
const input    = ref('')
const loading  = ref(false)
const chatRef  = ref(null)

const QUICK_Q = [
  { icon: '💀', text: '¿Qué es EternalBlue y cómo se explota?' },
  { icon: '🎯', text: '¿Cómo priorizo qué vulnerabilidades remediar?' },
  { icon: '🔐', text: '¿Qué implica SMB Signing deshabilitado?' },
  { icon: '🔑', text: '¿Qué hacer con credenciales por defecto en MySQL?' },
  { icon: '🌐', text: '¿Cómo hago un ataque de Pass-the-Hash?' },
  { icon: '🛡', text: '¿Cómo redacto un informe ejecutivo de auditoría?' },
]

function formatTime(ts) {
  if (!ts) return ''
  return new Date(ts).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
}

async function sendQuestion(q) { input.value = q; await send() }

function clearChat() { messages.value = []; input.value = '' }

async function scrollBottom() {
  await nextTick()
  if (chatRef.value) chatRef.value.scrollTo({ top: chatRef.value.scrollHeight, behavior: 'smooth' })
}

async function send() {
  const question = input.value.trim()
  if (!question || loading.value) return

  messages.value.push({ id: Date.now(), role: 'user', content: question, ts: Date.now() })
  input.value = ''
  await scrollBottom()

  const aiMsg = { id: Date.now() + 1, role: 'assistant', content: '', loading: true, ts: Date.now() }
  messages.value.push(aiMsg)
  loading.value = true
  await scrollBottom()

  try {
    const res = await api.post('/ai/ask/', { question })
    aiMsg.content = res.data.answer
    aiMsg.loading = false
  } catch (e) {
    aiMsg.content = '⚠ Error al contactar con Claude. Verifica la API key en la configuración.'
    aiMsg.loading = false
  } finally {
    loading.value = false
    await scrollBottom()
  }
}
</script>
