<template><div class="rounded-3xl border border-dashed border-gold/35 bg-gold/5 p-6"><label for="product-file" class="block text-sm font-semibold text-white">商品主图上传</label><p class="mt-2 text-sm text-slate-400">支持 JPG/PNG，建议上传清晰主图。</p><input id="product-file" type="file" accept=".jpg,.jpeg,.png,image/jpeg,image/png" class="mt-5 block w-full cursor-pointer rounded-2xl border border-white/10 bg-ink-2 p-3 text-sm text-slate-300 file:mr-4 file:rounded-full file:border-0 file:bg-gold file:px-4 file:py-2 file:text-sm file:font-bold file:text-ink" @change="handleChange" /><div v-if="file" class="mt-4 rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-sm text-slate-300">已选择：<span class="font-semibold text-gold">{{ file.name }}</span></div></div></template>
<script setup lang="ts">
defineProps<{ file: File | null }>()
const emit = defineEmits<{ fileChange: [file: File | null] }>()
function handleChange(event: Event) { emit('fileChange', (event.target as HTMLInputElement).files?.[0] ?? null) }
</script>
