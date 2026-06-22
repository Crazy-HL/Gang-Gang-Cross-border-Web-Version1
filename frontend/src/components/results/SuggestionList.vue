<template>
  <section class="rounded-[1.75rem] border border-orange-200 bg-[linear-gradient(135deg,#fff7ed_0%,#ffffff_72%,#eff6ff_100%)] p-6 shadow-sm shadow-orange-900/5">
    <div class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="text-sm font-black text-orange-800">下一步</p>
        <h2 class="mt-1 text-2xl font-black text-slate-950">建议先这样处理</h2>
      </div>
      <span class="rounded-full bg-white/80 px-4 py-2 text-xs font-black text-slate-600">按优先级查看</span>
    </div>

    <ol class="mt-6 grid gap-3">
      <li
        v-for="(suggestion, index) in suggestions"
        :key="suggestion"
        class="flex gap-4 rounded-2xl border border-white/80 bg-white/85 p-4 text-sm leading-6 text-slate-700 shadow-sm shadow-blue-900/5"
      >
        <span class="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-orange-500 text-xs font-black text-white">{{ index + 1 }}</span>
        <span class="pt-1">{{ suggestion }}</span>
      </li>
    </ol>
  </section>
</template>

<script setup lang="ts">
defineProps<{ suggestions: string[] }>()
</script>
