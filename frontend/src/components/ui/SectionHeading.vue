<template>
  <div class="mx-auto max-w-3xl text-center">
    <p class="text-sm font-bold uppercase tracking-[0.28em] text-blue-700">{{ eyebrow }}</p>
    <h2 class="mt-4 text-3xl font-black text-slate-950 md:text-5xl">{{ title }}</h2>
    <p v-if="description" class="mt-4 text-base leading-7 text-slate-500">{{ description }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{ eyebrow: string; title: string; description?: string }>()
</script>
