<template>
  <div class="rounded-[1.75rem] border border-slate-200/80 bg-white p-5 shadow-sm shadow-blue-900/5">
    <div class="flex items-start justify-between gap-4">
      <div>
        <p class="text-sm font-semibold text-slate-950">商品图片（可选）</p>
        <p class="mt-2 text-sm leading-6 text-slate-500">商品图、包装图或 Logo 图都可以。</p>
      </div>
      <span class="rounded-full bg-blue-50 px-3 py-1 text-xs font-bold text-blue-700">JPG / PNG</span>
    </div>

    <label for="product-file" class="mt-5 block cursor-pointer rounded-[1.5rem] border border-dashed border-blue-200 bg-blue-50/80 p-4 transition hover:border-blue-300 hover:bg-blue-50">
      <span class="block rounded-[1.25rem] bg-white/80 p-4">
        <span class="relative block h-36 overflow-hidden rounded-[1.15rem] bg-[linear-gradient(145deg,#dbeafe_0%,#ffffff_62%,#fff7ed_100%)]">
          <span class="absolute -left-8 -top-8 h-28 w-28 rounded-full bg-blue-200/55" />
          <span class="absolute -bottom-8 right-0 h-28 w-28 rounded-full bg-orange-100" />
          <span class="absolute left-7 top-7 h-20 w-20 rounded-[1.35rem] border border-blue-100 bg-white p-2 shadow-lg shadow-blue-900/10">
            <span class="block h-full rounded-[1rem] bg-blue-100" />
          </span>
          <span class="absolute bottom-6 left-16 right-7 rounded-2xl bg-white/95 px-4 py-3 shadow-md">
            <span class="block h-2.5 w-28 rounded-full bg-slate-200" />
            <span class="mt-2 block h-2 w-20 rounded-full bg-blue-100" />
          </span>
        </span>
        <span class="mt-4 block text-center text-base font-black text-slate-950">点击选择图片</span>
        <span class="mt-1 block text-center text-xs font-bold text-slate-400">也可以只填写右侧商品描述</span>
      </span>
    </label>

    <input id="product-file" type="file" accept=".jpg,.jpeg,.png,image/jpeg,image/png" class="sr-only" @change="handleChange" />

    <div v-if="file" class="mt-4 rounded-2xl border border-blue-100 bg-blue-50 p-4 text-sm text-slate-600">
      已选择：<span class="font-semibold text-slate-800">{{ file.name }}</span>
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
