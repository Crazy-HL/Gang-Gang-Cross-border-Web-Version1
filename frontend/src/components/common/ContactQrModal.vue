<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-50 grid place-items-center bg-slate-950/55 px-5"
      role="dialog"
      aria-modal="true"
      aria-labelledby="contact-qr-title"
      tabindex="-1"
      @click.self="$emit('close')"
      @keydown.esc="$emit('close')"
    >
      <div class="w-full max-w-sm rounded-[2rem] bg-white p-6 shadow-2xl">
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-sm font-black text-blue-700">联系港港跨境</p>
            <h2 id="contact-qr-title" class="mt-2 text-xl font-black text-slate-950">扫码添加顾问</h2>
          </div>
          <button type="button" class="rounded-full border border-slate-200 px-3 py-1 text-sm font-bold text-slate-700 transition hover:border-blue-200 hover:text-blue-700" @click="$emit('close')">
            关闭
          </button>
        </div>
        <div class="mt-5 grid place-items-center rounded-2xl border border-blue-100 bg-blue-50 p-4">
          <img src="/wechat-qrcode-cropped.jpg" alt="港港跨境微信二维码" class="aspect-square w-56 rounded-2xl bg-white object-contain" />
        </div>
        <p class="mt-4 text-sm leading-6 text-slate-600">请备注报告编号，方便顾问快速定位你的资料。</p>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
defineProps<{ open: boolean }>()
defineEmits<{ close: [] }>()
</script>
