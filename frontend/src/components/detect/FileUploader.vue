<template>
  <div class="flex h-full min-h-[24rem] flex-col rounded-[1.75rem] border border-blue-100 bg-[linear-gradient(145deg,#ffffff_0%,#f3f9ff_58%,#fff7ed_100%)] p-5 shadow-sm shadow-blue-900/5">
    <div class="flex items-start justify-between gap-4">
      <div>
        <p class="text-sm font-black text-slate-950">商品图片（可选）</p>
        <p class="mt-2 text-sm leading-6 text-slate-500">商品图、包装图或 Logo 图都可以。</p>
      </div>
      <span class="shrink-0 rounded-full border border-blue-100 bg-blue-50 px-3 py-1 text-xs font-bold text-blue-700">JPG / PNG</span>
    </div>

    <label for="product-file" class="mt-4 flex flex-1 cursor-pointer rounded-[1.35rem] border border-dashed border-blue-200 bg-blue-50/75 p-3 transition hover:border-blue-300 hover:bg-blue-50">
      <span class="relative flex min-h-[12rem] w-full flex-col items-center justify-center overflow-hidden rounded-[1.1rem] border border-white/80 bg-white/85 px-5 py-6 text-center shadow-inner shadow-blue-100/50">
        <span class="pointer-events-none absolute -right-12 -top-14 h-40 w-40 rounded-full bg-orange-200/35 blur-3xl" />
        <span class="pointer-events-none absolute -bottom-14 left-8 h-44 w-44 rounded-full bg-blue-200/45 blur-3xl" />

        <span class="relative grid h-16 w-16 place-items-center rounded-2xl bg-[linear-gradient(145deg,#dbeafe_0%,#ffffff_62%,#fff7ed_100%)] ring-1 ring-blue-100">
          <svg class="h-8 w-8 text-blue-700" viewBox="0 0 48 48" fill="none" aria-hidden="true">
            <rect x="8" y="10" width="32" height="28" rx="7" stroke="currentColor" stroke-width="3" />
            <circle cx="18" cy="20" r="3" fill="currentColor" />
            <path d="M12 34L21 26L28 32L32 28L38 34" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </span>

        <span class="relative mt-4 max-w-full">
          <span class="block truncate text-base font-black text-slate-950">{{ file ? file.name : '上传商品图片' }}</span>
          <span class="mt-2 block text-sm font-bold leading-6 text-slate-500">
            点击选择图片，或只填写右侧商品描述
          </span>
        </span>
      </span>
    </label>

    <input id="product-file" type="file" accept=".jpg,.jpeg,.png,image/jpeg,image/png" class="sr-only" @change="handleChange" />

    <div class="mt-3 min-h-11 rounded-2xl border px-4 py-2.5 text-sm font-bold" :class="file ? 'border-blue-100 bg-blue-50 text-blue-700' : 'border-white/80 bg-white/75 text-slate-500'">
      {{ file ? '已选择图片，可以开始预检' : '支持 JPG / PNG 图片上传' }}
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ file: File | null }>()
const emit = defineEmits<{ fileChange: [file: File | null] }>()

function handleChange(event: Event) {
  emit('fileChange', (event.target as HTMLInputElement).files?.[0] ?? null)
}
</script>
