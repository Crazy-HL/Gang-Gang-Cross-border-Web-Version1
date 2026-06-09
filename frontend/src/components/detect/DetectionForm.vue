<template>
  <form class="space-y-8 rounded-[2rem] border border-white/10 bg-panel/75 p-6 shadow-2xl md:p-8" @submit.prevent="handleSubmit">
    <section><h2 class="text-xl font-bold text-white">步骤一：选择检测类型</h2><div class="mt-5 grid gap-4 md:grid-cols-3"><label v-for="option in detectionOptions" :key="option.value" class="cursor-pointer rounded-3xl border border-white/10 bg-white/[0.04] p-5 transition hover:border-gold/40"><input v-model="formData.detectionType" type="radio" name="detectionType" :value="option.value" :aria-label="option.label" class="sr-only" /><span class="block text-base font-bold text-white">{{ option.label }}</span><span class="mt-2 block text-sm leading-6 text-slate-400">{{ option.description }}</span></label></div></section>
    <section class="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]"><FileUploader :file="file" @file-change="file = $event" /><div class="grid gap-5"><label class="block text-sm font-semibold text-white">商品链接<input v-model="formData.productLink" aria-label="商品链接" placeholder="https://www.amazon.com/dp/..." class="mt-2 w-full rounded-2xl border border-white/10 bg-ink-2 px-4 py-3 text-slate-100 placeholder:text-slate-600" /></label><label class="block text-sm font-semibold text-white">商品标题/卖点文案<textarea v-model="formData.title" aria-label="商品标题/卖点文案" rows="3" class="mt-2 w-full rounded-2xl border border-white/10 bg-ink-2 px-4 py-3 text-slate-100 placeholder:text-slate-600" placeholder="输入商品标题、五点描述或详情页核心文案" /></label></div></section>
    <section class="grid gap-5 md:grid-cols-3"><label class="block text-sm font-semibold text-white">品牌名<input v-model="formData.brand" aria-label="品牌名" class="mt-2 w-full rounded-2xl border border-white/10 bg-ink-2 px-4 py-3 text-slate-100" /></label><label class="block text-sm font-semibold text-white">商品类目<select v-model="formData.category" aria-label="商品类目" class="mt-2 w-full rounded-2xl border border-white/10 bg-ink-2 px-4 py-3 text-slate-100"><option value="">请选择</option><option v-for="category in categories" :key="category.value" :value="category.value">{{ category.label }}</option></select></label><label class="block text-sm font-semibold text-white">目标市场<select v-model="formData.market" aria-label="目标市场" class="mt-2 w-full rounded-2xl border border-white/10 bg-ink-2 px-4 py-3 text-slate-100"><option value="">请选择</option><option v-for="market in markets" :key="market.value" :value="market.value">{{ market.label }}</option></select></label></section>
    <div v-if="validation.errors.length > 0" class="rounded-2xl border border-ember/30 bg-ember/10 p-4 text-sm text-orange-200">{{ validation.errors[0] }}</div>
    <div v-if="isSubmitting" class="rounded-2xl border border-gold/25 bg-gold/10 p-4 text-sm font-semibold text-gold">{{ currentStage }}，请稍候...</div>
    <button type="submit" :disabled="!validation.isValid || isSubmitting" class="w-full rounded-full bg-gold px-6 py-4 text-sm font-black text-ink shadow-glow transition hover:bg-amber-300 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400 disabled:shadow-none">提交检测</button>
  </form>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import FileUploader from '@/components/detect/FileUploader.vue'
import { createJob, getOptions, runJob, uploadJobFile } from '@/api/client'
import { validateDetectionForm } from '@/utils/validation'
import type { DetectionFormInput, DetectionType, SelectOption } from '@/types/domain'

const router = useRouter()
const file = ref<File | null>(null)
const currentStage = ref('')
const isSubmitting = ref(false)
const categories = ref<SelectOption[]>([])
const markets = ref<SelectOption[]>([])
const formData = reactive<DetectionFormInput>({ detectionType: '', brand: '', category: '', market: '', productLink: '', title: '', hasFile: false })
const detectionOptions: { value: DetectionType; label: string; description: string }[] = [
  { value: 'trademark', label: '商标检测', description: '品牌词、图形商标、近似名称冲突' },
  { value: 'design', label: '外观检测', description: '商品形态、包装、关键视觉元素' },
  { value: 'copyright', label: '版权检测', description: '图片、文案、角色和素材版权风险' }
]
const validation = computed(() => validateDetectionForm({ ...formData, hasFile: Boolean(file.value), file: file.value ? { name: file.value.name, type: file.value.type, size: file.value.size } : undefined }))

onMounted(async () => { const options = await getOptions(); categories.value = options.categories; markets.value = options.markets })
async function handleSubmit() {
  if (!validation.value.isValid || isSubmitting.value) return
  isSubmitting.value = true
  currentStage.value = '解析中'
  const input = { ...formData, hasFile: Boolean(file.value), file: file.value ? { name: file.value.name, type: file.value.type, size: file.value.size } : undefined }
  const created = await createJob(input)
  if (file.value) await uploadJobFile(created.jobId, file.value)
  currentStage.value = '检测中'
  await runJob(created.jobId)
  currentStage.value = '报告生成中'
  window.setTimeout(() => router.push(`/results/${created.jobId}`), 240)
}
</script>
