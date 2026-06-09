<template>
  <RouterLink :to="href" :class="classes"><slot /></RouterLink>
</template>

<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{ href: string; variant?: 'primary' | 'secondary' }>()
const classes = computed(() => props.variant === 'secondary' ? 'rounded-full border border-white/15 px-6 py-3 text-sm font-bold text-white transition hover:border-gold hover:text-gold' : 'rounded-full bg-gold px-6 py-3 text-sm font-black text-ink shadow-glow transition hover:bg-amber-300')
</script>
