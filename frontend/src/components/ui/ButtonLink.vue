<template>
  <RouterLink :to="href" :class="classes"><slot /></RouterLink>
</template>

<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{ href: string; variant?: 'primary' | 'secondary' }>()
const classes = computed(() =>
  props.variant === 'secondary'
    ? 'rounded-full border border-slate-200 bg-white px-6 py-3 text-sm font-bold text-slate-950 shadow-sm transition hover:border-blue-300 hover:bg-blue-50 hover:text-blue-700'
    : 'rounded-full bg-gold px-6 py-3 text-sm font-black text-white shadow-glow transition hover:bg-blue-600'
)
</script>
