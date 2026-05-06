<template>
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden" style="background:#060910;">

    <!-- Animated background grid -->
    <div class="absolute inset-0" style="background-image:linear-gradient(rgba(0,212,255,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(0,212,255,0.03) 1px,transparent 1px);background-size:48px 48px;"></div>

    <!-- Radial glow center -->
    <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
      <div style="width:600px;height:600px;background:radial-gradient(circle,rgba(0,212,255,0.06) 0%,transparent 70%);border-radius:50%;"></div>
    </div>

    <!-- Scan line animation -->
    <div class="absolute inset-x-0 animate-scan-line pointer-events-none" style="height:1px;background:linear-gradient(90deg,transparent,rgba(0,212,255,0.4),transparent);position:absolute;"></div>

    <!-- Corner decorations -->
    <div class="absolute top-8 left-8 text-[10px] font-mono" style="color:#1e2d3d;letter-spacing:0.15em;">SYS::VANTAGE-OPS v2.1.0</div>
    <div class="absolute top-8 right-8 text-[10px] font-mono" style="color:#1e2d3d;letter-spacing:0.1em;">{{ dateStr }}</div>
    <div class="absolute bottom-8 left-8 text-[10px] font-mono" style="color:#1e2d3d;">AUTHORIZED ACCESS ONLY</div>
    <div class="absolute bottom-8 right-8 flex items-center gap-2">
      <span class="w-1.5 h-1.5 rounded-full bg-green animate-pulse inline-block"></span>
      <span class="text-[10px] font-mono" style="color:#1e2d3d;letter-spacing:0.1em;">SECURE CHANNEL</span>
    </div>

    <!-- Main card -->
    <div class="relative z-10 w-full max-w-sm px-4 animate-entry">

      <!-- Logo mark -->
      <div class="text-center mb-10">
        <div class="inline-flex flex-col items-center">
          <div class="w-16 h-16 rounded-2xl mb-5 flex items-center justify-center relative"
            style="background:linear-gradient(135deg,rgba(0,212,255,0.12),rgba(0,212,255,0.04));border:1px solid rgba(0,212,255,0.25);"
            :class="{ 'glow-cyan': !loading, 'animate-pulse-cyan': loading }">
            <!-- Shield icon -->
            <svg class="w-8 h-8 text-cyan" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
            </svg>
            <!-- Corner marks -->
            <span class="absolute top-1 left-1 w-2 h-2 border-l border-t rounded-none" style="border-color:rgba(0,212,255,0.5);"></span>
            <span class="absolute top-1 right-1 w-2 h-2 border-r border-t" style="border-color:rgba(0,212,255,0.5);"></span>
            <span class="absolute bottom-1 left-1 w-2 h-2 border-l border-b" style="border-color:rgba(0,212,255,0.5);"></span>
            <span class="absolute bottom-1 right-1 w-2 h-2 border-r border-b" style="border-color:rgba(0,212,255,0.5);"></span>
          </div>
          <h1 style="font-family:'Rajdhani',sans-serif;font-size:36px;font-weight:700;color:#fff;letter-spacing:0.12em;line-height:1;">VANTAGE</h1>
          <p class="mt-1.5 text-xs uppercase tracking-widest" style="color:#4b6277;font-family:'Rajdhani',sans-serif;letter-spacing:0.2em;">Network Audit Platform</p>
        </div>
      </div>

      <!-- Form -->
      <div style="background:linear-gradient(135deg,rgba(13,17,23,0.97),rgba(17,24,39,0.97));border:1px solid #1e2d3d;border-radius:16px;padding:28px;box-shadow:0 24px 80px rgba(0,0,0,0.7);">

        <!-- Form header -->
        <div class="flex items-center gap-2 mb-6">
          <div class="w-1 h-5 rounded-full bg-cyan"></div>
          <span style="font-family:'Rajdhani',sans-serif;font-size:13px;font-weight:700;letter-spacing:0.1em;color:#8ba5bc;text-transform:uppercase;">AUTENTICACIÓN</span>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block mb-1.5 text-xs uppercase tracking-wider" style="color:#4b6277;font-family:'Rajdhani',sans-serif;font-weight:700;letter-spacing:0.12em;">Operador</label>
            <div class="relative">
              <input v-model="form.username" type="text" placeholder="username" class="input pl-9" autocomplete="username" required />
              <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5" style="color:#4b6277;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
            </div>
          </div>
          <div>
            <label class="block mb-1.5 text-xs uppercase tracking-wider" style="color:#4b6277;font-family:'Rajdhani',sans-serif;font-weight:700;letter-spacing:0.12em;">Clave de Acceso</label>
            <div class="relative">
              <input v-model="form.password" :type="showPwd ? 'text' : 'password'" placeholder="••••••••••" class="input pl-9 pr-9" autocomplete="current-password" required />
              <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5" style="color:#4b6277;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
              </svg>
              <button type="button" @click="showPwd = !showPwd" class="absolute right-3 top-1/2 -translate-y-1/2" style="color:#4b6277;">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path v-if="!showPwd" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                  <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Error -->
          <Transition name="v">
            <div v-if="error" class="flex items-center gap-2 px-3 py-2 rounded-lg text-xs" style="background:rgba(255,56,100,0.1);border:1px solid rgba(255,56,100,0.2);color:#ff3864;">
              <svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
              {{ error }}
            </div>
          </Transition>

          <button type="submit" :disabled="loading"
            class="btn-primary w-full justify-center mt-2"
            style="height:44px;font-size:14px;letter-spacing:0.1em;">
            <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"/>
            </svg>
            {{ loading ? 'AUTENTICANDO...' : 'ACCEDER AL SISTEMA' }}
          </button>
        </form>
      </div>

      <p class="text-center mt-6 text-[10px] uppercase tracking-widest" style="color:#2d4356;font-family:'Rajdhani',sans-serif;letter-spacing:0.15em;">
        Uso exclusivo para auditorías autorizadas
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth    = useAuthStore()
const router  = useRouter()
const form    = reactive({ username: '', password: '' })
const loading = ref(false)
const error   = ref('')
const showPwd = ref(false)
const dateStr = ref('')

onMounted(() => {
  dateStr.value = new Date().toISOString().split('T')[0]
})

async function handleLogin() {
  loading.value = true
  error.value   = ''
  try {
    await auth.login(form.username, form.password)
    router.push('/')
  } catch {
    error.value = 'Credenciales incorrectas o acceso denegado'
  } finally {
    loading.value = false
  }
}
</script>
