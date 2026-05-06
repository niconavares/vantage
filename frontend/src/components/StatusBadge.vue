<template>
  <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wide"
    :class="styles[status] || styles.default">
    <span class="w-1.5 h-1.5 rounded-full" :class="dot[status] || dot.default"></span>
    {{ labels[status] || status }}
  </span>
</template>

<script setup>
defineProps({ status: String })
const labels  = { planning: 'Planif.', active: 'Activo', paused: 'Pausado', completed: 'Completado', archived: 'Archivado' }
const styles  = {
  planning:  'bg-muted/20 text-muted',
  active:    'bg-cyan/10 text-cyan',
  paused:    'bg-yellow/10 text-yellow',
  completed: 'bg-green/10 text-green',
  archived:  'bg-border text-muted',
  default:   'bg-muted/20 text-muted',
}
const dot = {
  active:    'bg-cyan animate-pulse',
  completed: 'bg-green',
  paused:    'bg-yellow',
  default:   'bg-muted',
}
</script>
