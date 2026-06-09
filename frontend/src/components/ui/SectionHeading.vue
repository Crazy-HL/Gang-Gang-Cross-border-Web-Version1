<template>
  <div class="mx-auto max-w-3xl text-center">
    <p class="text-sm font-bold uppercase tracking-[0.35em] text-gold">{{ eyebrow }}</p>
    <h2 class="mt-4 text-3xl font-black text-white md:text-5xl">{{ title }}</h2>
    <p v-if="description" class="mt-4 text-base leading-7 text-slate-400">{{ description }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{ eyebrow: string; title: string; description?: string }>()
</script>
