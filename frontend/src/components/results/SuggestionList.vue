<template><section class="rounded-3xl border border-gold/20 bg-gold/10 p-6"><h2 class="text-xl font-bold text-white">处理建议</h2><ol class="mt-5 space-y-3"><li v-for="(suggestion, index) in suggestions" :key="suggestion" class="flex gap-3 text-sm leading-6 text-slate-200"><span class="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-gold text-xs font-black text-ink">{{ index + 1 }}</span><span>{{ suggestion }}</span></li></ol></section></template>
<script setup lang="ts">
defineProps<{ suggestions: string[] }>()
</script>
