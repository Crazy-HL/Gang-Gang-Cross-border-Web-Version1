<template>
  <section class="relative overflow-hidden bg-[radial-gradient(circle_at_75%_10%,rgba(251,146,60,0.18),transparent_28%),linear-gradient(135deg,#ffffff_0%,#eef7ff_50%,#fff8ed_100%)] px-5 pb-12 pt-20 lg:px-8 lg:pb-14 lg:pt-24">
    <div class="pointer-events-none absolute inset-x-0 top-0 h-24 bg-white/70" />
    <div class="pointer-events-none absolute -right-20 top-24 h-72 w-72 rounded-full bg-blue-200/35 blur-3xl" />
    <div class="pointer-events-none absolute bottom-10 left-6 h-64 w-64 rounded-full bg-orange-200/30 blur-3xl" />

    <div class="relative mx-auto grid max-w-7xl items-start gap-12 lg:grid-cols-[1fr_0.92fr]">
      <div>
        <p class="inline-flex rounded-full border border-blue-200 bg-white/80 px-4 py-2 text-sm font-bold text-blue-700 shadow-sm shadow-blue-900/5">
          商品上架前，先做合规预检
        </p>
        <h1 class="mt-7 max-w-4xl text-5xl font-black leading-tight tracking-tight text-slate-950 md:text-7xl">
          上架前先做预检
          <span class="block text-blue-600">降低侵权风险</span>
        </h1>
        <p class="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
          把商品图片、标题或详情文案发来，我们帮你初步判断商标、外观、版权等常见风险。
        </p>

        <div class="mt-9 flex flex-col gap-4 sm:flex-row">
          <ButtonLink href="/detect">免费检测</ButtonLink>
          <ButtonLink href="/reports/1001" variant="secondary">查看预检示例</ButtonLink>
        </div>

        <div class="mt-9 grid max-w-xl gap-3 sm:grid-cols-3">
          <div v-for="metric in metrics" :key="metric.label" class="rounded-2xl border border-white/80 bg-white/70 p-4 shadow-sm shadow-blue-900/5 backdrop-blur">
            <p class="text-lg font-black text-slate-950">{{ metric.value }}</p>
            <p class="mt-1 text-xs font-bold text-slate-500">{{ metric.label }}</p>
          </div>
        </div>
      </div>

      <div class="relative">
        <form class="rounded-[2rem] border border-white/80 bg-white/80 p-2.5 shadow-2xl shadow-blue-900/15 backdrop-blur-xl" @submit.prevent="handleHeroSubmit">
          <div class="relative overflow-hidden rounded-[1.5rem] border border-blue-100 bg-[linear-gradient(145deg,#ffffff_0%,#f3f9ff_58%,#fff7ed_100%)] p-3">
            <div class="pointer-events-none absolute -right-14 -top-16 h-44 w-44 rounded-full bg-orange-200/35 blur-3xl" />
            <div class="pointer-events-none absolute -bottom-16 left-12 h-48 w-48 rounded-full bg-blue-200/45 blur-3xl" />
            <div class="flex items-center gap-2">
              <span class="h-3 w-3 rounded-full bg-orange-400" />
              <span class="h-3 w-3 rounded-full bg-amber-300" />
              <span class="h-3 w-3 rounded-full bg-blue-400" />
            </div>

            <div class="relative mt-3 flex items-start justify-between gap-4">
              <div>
                <p class="text-sm font-bold text-slate-500">上架合规预检</p>
                <h2 class="mt-1 text-2xl font-black text-slate-950">免费检测</h2>
              </div>
              <div class="flex flex-wrap justify-end gap-2">
                <label class="inline-flex items-center gap-1.5 text-xs font-bold text-blue-700">
                  <span>国家</span>
                  <select
                    v-model="formData.market"
                    aria-label="目标国家"
                    class="max-w-24 rounded-full border border-blue-100 bg-blue-50 px-2.5 py-1.5 text-xs font-bold text-blue-700 outline-none transition focus:border-blue-300 focus:bg-white focus:ring-4 focus:ring-blue-100"
                  >
                    <option value="">请选择</option>
                    <option value="美国">美国</option>
                    <option value="欧盟">欧盟</option>
                    <option value="英国">英国</option>
                    <option value="加拿大">加拿大</option>
                    <option value="澳大利亚">澳大利亚</option>
                    <option value="日本">日本</option>
                    <option value="全球">暂不确定</option>
                  </select>
                </label>
                <label class="inline-flex items-center gap-1.5 text-xs font-bold text-orange-800">
                  <span>平台</span>
                  <select
                    v-model="platform"
                    aria-label="目标平台"
                    class="max-w-24 rounded-full border border-orange-100 bg-orange-50 px-2.5 py-1.5 text-xs font-bold text-orange-800 outline-none transition focus:border-orange-300 focus:bg-white focus:ring-4 focus:ring-orange-100"
                  >
                    <option value="">请选择</option>
                    <option value="亚马逊">亚马逊</option>
                    <option value="希音">希音</option>
                    <option value="Temu">Temu</option>
                    <option value="TikTok Shop">TikTok Shop</option>
                    <option value="速卖通">速卖通</option>
                    <option value="eBay">eBay</option>
                    <option value="独立站">独立站</option>
                    <option value="暂不确定">暂不确定</option>
                  </select>
                </label>
              </div>
            </div>

            <div class="relative mt-3 overflow-hidden rounded-[1.5rem] border border-blue-100 bg-white/85 p-3.5 shadow-inner shadow-blue-100/50">
              <div class="pointer-events-none absolute -right-10 -top-12 h-40 w-40 rounded-full bg-orange-200/35 blur-3xl" />
              <div class="pointer-events-none absolute -bottom-12 left-8 h-44 w-44 rounded-full bg-blue-200/45 blur-3xl" />

              <div class="relative grid gap-3">
                <label for="hero-product-file" class="block cursor-pointer rounded-[1.25rem] border border-dashed border-blue-200 bg-blue-50/80 p-3 transition hover:border-blue-300 hover:bg-blue-50">
                  <span class="flex items-center gap-3 rounded-[1rem] bg-white/85 p-3">
                    <span class="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-[linear-gradient(145deg,#dbeafe_0%,#ffffff_62%,#fff7ed_100%)] ring-1 ring-blue-100">
                      <svg class="h-6 w-6 text-blue-700" viewBox="0 0 48 48" fill="none" aria-hidden="true">
                        <rect x="8" y="10" width="32" height="28" rx="7" stroke="currentColor" stroke-width="3" />
                        <circle cx="18" cy="20" r="3" fill="currentColor" />
                        <path d="M12 34L21 26L28 32L32 28L38 34" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
                      </svg>
                    </span>
                    <span class="min-w-0">
                      <span class="block truncate text-sm font-black text-slate-950">{{ file ? file.name : '上传商品图片' }}</span>
                      <span class="mt-1 block text-xs font-bold text-slate-500">JPG / PNG，或只填写商品描述</span>
                    </span>
                  </span>
                </label>
                <input id="hero-product-file" type="file" accept=".jpg,.jpeg,.png,image/jpeg,image/png" class="sr-only" @change="handleFileChange" />

                <label class="block rounded-[1.25rem] border border-slate-200/80 bg-white p-3.5 shadow-sm shadow-blue-900/5">
                  <span class="text-sm font-black text-slate-950">商品描述</span>
                  <textarea
                    v-model="formData.title"
                    rows="2"
                    aria-label="商品描述"
                    class="mt-2 w-full resize-none rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm leading-6 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-300 focus:bg-white focus:ring-4 focus:ring-blue-100"
                    placeholder="填写商品标题、详情文案、包装文字，或你担心的风险点"
                  />
                </label>

                <div v-if="isSubmitting" class="rounded-[1.25rem] border border-blue-100 bg-[linear-gradient(135deg,#eff6ff_0%,#ffffff_60%,#fff7ed_100%)] p-3 shadow-sm shadow-blue-900/5">
                  <div class="flex items-center justify-between gap-3">
                    <span class="text-xs font-black text-slate-950">{{ progressLabel }}</span>
                    <span class="text-xs font-black text-blue-700">{{ progress }}%</span>
                  </div>
                  <div class="mt-2 h-2.5 overflow-hidden rounded-full bg-slate-100">
                    <div
                      class="h-full rounded-full bg-[linear-gradient(90deg,#2563eb_0%,#38bdf8_56%,#fb923c_100%)] transition-all duration-500"
                      :style="{ width: `${progress}%` }"
                    />
                  </div>
                </div>

                <div class="grid gap-3 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center">
                  <p class="min-h-5 text-xs font-bold sm:text-sm" :class="messageTone">
                    {{ message }}
                  </p>
                  <button
                    type="submit"
                    :disabled="!validation.isValid || isSubmitting"
                    class="rounded-full bg-gold px-6 py-3 text-sm font-black text-white shadow-glow transition hover:bg-blue-600 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-500 disabled:shadow-none"
                  >
                    {{ isSubmitting ? '提交中...' : '免费检测' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </form>

      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import ButtonLink from '@/components/ui/ButtonLink.vue'
import { createJob, getJobStatus, runJob, uploadJobFile } from '@/api/client'
import { validateDetectionForm } from '@/utils/validation'
import type { DetectionFormInput } from '@/types/domain'

const router = useRouter()
const file = ref<File | null>(null)
const platform = ref('')
const isSubmitting = ref(false)
const progress = ref(0)
const progressLabel = ref('')
const message = ref('上传图片或填写一段描述即可开始。')
const messageTone = ref('text-slate-500')
const formData = reactive<DetectionFormInput>({ detectionType: '', brand: '', category: '', market: '', productLink: '', title: '', hasFile: false })
const validation = computed(() => validateDetectionForm({ ...formData, hasFile: Boolean(file.value), file: file.value ? { name: file.value.name, type: file.value.type, size: file.value.size } : undefined }))

const metrics = [
  { value: '提交资料', label: '图片或文案' },
  { value: '初步预检', label: '商标/外观/版权' },
  { value: '风险建议', label: '下一步怎么做' }
]

function sleep(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms))
}

function handleFileChange(event: Event) {
  file.value = (event.target as HTMLInputElement).files?.[0] ?? null
  if (validation.value.errors[0]) {
    message.value = validation.value.errors[0]
    messageTone.value = 'text-orange-800'
    return
  }
  message.value = file.value ? '图片已选择，可以开始预检。' : '上传图片或填写一段描述即可开始。'
  messageTone.value = 'text-slate-500'
}

async function waitForReport(jobId: string) {
  for (let attempt = 0; attempt < 40; attempt += 1) {
    const job = await getJobStatus(jobId)

    if (job.status === 'done') {
      progress.value = 100
      progressLabel.value = '报告已生成'
      message.value = '报告已生成，正在打开...'
      await sleep(350)
      return
    }

    if (job.status === 'failed') {
      throw new Error('report generation failed')
    }

    const base = job.status === 'processing' ? 58 : 46
    progress.value = Math.min(94, base + attempt * 3)
    progressLabel.value = job.status === 'processing' ? '正在生成报告' : '任务已提交，正在排队'
    message.value = job.status === 'processing' ? '正在分析商品资料，请稍候。' : '任务已提交，正在准备检测。'
    await sleep(1500)
  }

  throw new Error('report generation timeout')
}

async function handleHeroSubmit() {
  if (!validation.value.isValid || isSubmitting.value) {
    message.value = validation.value.errors[0] ?? '请先提交商品资料。'
    messageTone.value = 'text-orange-800'
    return
  }

  isSubmitting.value = true
  progress.value = 12
  progressLabel.value = '正在提交资料'
  message.value = '正在提交资料...'
  messageTone.value = 'text-blue-700'

  try {
    const title = [platform.value ? `目标平台：${platform.value}` : '', formData.title.trim()].filter(Boolean).join('\n')
    const input = { ...formData, title, productLink: '', hasFile: Boolean(file.value), file: file.value ? { name: file.value.name, type: file.value.type, size: file.value.size } : undefined }
    const created = await createJob(input)
    progress.value = file.value ? 28 : 42
    progressLabel.value = file.value ? '正在上传图片' : '正在启动检测'
    if (file.value) {
      await uploadJobFile(created.jobId, file.value)
      progress.value = 46
      progressLabel.value = '正在启动检测'
    }
    await runJob(created.jobId)
    progress.value = 56
    progressLabel.value = '正在生成报告'
    await waitForReport(created.jobId)
    await router.push(`/results/${created.jobId}`)
  } catch (error) {
    const reason = error instanceof Error ? error.message : ''
    if (reason.includes('401') || reason.includes('403')) {
      await router.push(`/auth?redirect=${encodeURIComponent('/detect')}`)
      return
    }
    message.value = reason.includes('failed') ? '报告生成失败，请重新提交。' : reason.includes('timeout') ? '报告生成时间较长，请稍后查看任务。' : '提交失败，请稍后再试。'
    messageTone.value = 'text-orange-800'
  } finally {
    isSubmitting.value = false
  }
}
</script>
