<template>
  <form class="overflow-hidden rounded-[2rem] border border-white/80 bg-white/85 shadow-2xl shadow-blue-900/12 backdrop-blur" @submit.prevent="handleSubmit">
    <div class="grid lg:grid-cols-[1fr_0.42fr]">
      <section class="p-5 md:p-7">
        <div class="rounded-[1.75rem] border border-blue-100 bg-[linear-gradient(145deg,#ffffff_0%,#f3f9ff_66%,#fff7ed_100%)] p-5">
          <p class="text-sm font-bold text-blue-700">资料提交</p>
          <h2 class="mt-2 text-2xl font-black text-slate-950 md:text-3xl">上传图片，或填写商品文案</h2>
          <p class="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
            两种方式任选一种，也可以一起提交。
          </p>
        </div>

        <div class="mt-6 rounded-[1.75rem] border border-blue-100 bg-white p-5 shadow-sm shadow-blue-900/5">
          <label class="block text-sm font-black text-slate-950">
            目标国家
            <select
              v-model="formData.market"
              class="mt-3 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-bold text-slate-900 outline-none transition focus:border-blue-300 focus:bg-white focus:ring-4 focus:ring-blue-100"
              aria-label="目标国家"
            >
              <option value="">请选择目标国家</option>
              <option value="美国">美国</option>
              <option value="欧盟">欧盟</option>
              <option value="英国">英国</option>
              <option value="加拿大">加拿大</option>
              <option value="澳大利亚">澳大利亚</option>
              <option value="日本">日本</option>
              <option value="全球">暂不确定</option>
            </select>
          </label>
        </div>

        <div class="mt-6 grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
          <FileUploader :file="file" @file-change="file = $event" />

          <label class="block rounded-[1.75rem] border border-slate-200/80 bg-white p-5 text-sm font-semibold text-slate-950 shadow-sm shadow-blue-900/5">
            商品描述（可选）
            <textarea
              v-model="formData.title"
              aria-label="商品描述"
              rows="9"
              class="mt-3 w-full resize-none rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-300 focus:bg-white focus:ring-4 focus:ring-blue-100"
              placeholder="例如：商品标题、详情描述、包装文案，或你担心的风险点"
            />
          </label>
        </div>

        <div v-if="validation.errors.length > 0" class="mt-6 rounded-2xl border border-orange-200 bg-orange-50 p-4 text-sm font-bold text-orange-800">
          {{ validation.errors[0] }}
        </div>
        <div v-if="isSubmitting" class="mt-6 rounded-2xl border border-blue-200 bg-[linear-gradient(135deg,#eff6ff_0%,#ffffff_65%,#fff7ed_100%)] p-4">
          <div class="flex items-center justify-between gap-3">
            <span class="text-sm font-black text-blue-700">{{ currentStage }}</span>
            <span class="text-sm font-black text-blue-700">{{ progress }}%</span>
          </div>
          <div class="mt-3 h-2.5 overflow-hidden rounded-full bg-slate-100">
            <div
              class="h-full rounded-full bg-[linear-gradient(90deg,#2563eb_0%,#38bdf8_58%,#fb923c_100%)] transition-all duration-500"
              :style="{ width: `${progress}%` }"
            />
          </div>
        </div>
      </section>

      <aside class="border-t border-slate-200/80 bg-slate-50/80 p-5 md:p-7 lg:border-l lg:border-t-0">
        <div class="rounded-[1.75rem] border border-white bg-white p-5 shadow-xl shadow-blue-900/8">
          <p class="text-sm font-black text-slate-950">预检摘要</p>
          <div class="mt-5 grid gap-3">
            <div v-for="item in summaryItems" :key="item.title" class="rounded-2xl border border-slate-200/70 bg-white px-4 py-3">
              <div class="flex items-center justify-between gap-3">
                <p class="text-sm font-bold text-slate-950">{{ item.title }}</p>
                <span class="rounded-full px-2.5 py-1 text-xs font-bold" :class="item.tone">{{ item.status }}</span>
              </div>
              <p class="mt-1 text-xs font-bold text-slate-500">{{ item.desc }}</p>
            </div>
          </div>
        </div>

        <div class="mt-4 rounded-[1.75rem] border border-orange-200 bg-orange-50 p-5">
          <p class="text-xs font-bold text-orange-800">提交后你会得到</p>
          <h3 class="mt-2 text-xl font-black text-slate-950">一份预检建议</h3>
          <p class="mt-2 text-sm leading-6 text-slate-600">重点风险会用橙色标出。</p>
        </div>

        <button
          type="submit"
          :disabled="!validation.isValid || isSubmitting"
          class="mt-5 w-full rounded-full bg-gold px-8 py-4 text-sm font-black text-white shadow-glow transition hover:bg-blue-600 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-500 disabled:shadow-none"
        >
          开始预检
        </button>
        <p class="mt-3 text-center text-xs font-bold text-slate-500">请选择目标国家，并上传图片或填写商品描述</p>
      </aside>
    </div>
  </form>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import FileUploader from '@/components/detect/FileUploader.vue'
import { createJob, getJobStatus, runJob, uploadJobFile } from '@/api/client'
import { validateDetectionForm } from '@/utils/validation'
import type { DetectionFormInput } from '@/types/domain'

const router = useRouter()
const file = ref<File | null>(null)
const currentStage = ref('')
const progress = ref(0)
const isSubmitting = ref(false)
const formData = reactive<DetectionFormInput>({ detectionType: '', brand: '', category: '', market: '', productLink: '', title: '', hasFile: false })
const validation = computed(() => validateDetectionForm({ ...formData, hasFile: Boolean(file.value), file: file.value ? { name: file.value.name, type: file.value.type, size: file.value.size } : undefined }))

const summaryItems = [
  { title: '商标近似', desc: '品牌名、Logo 是否容易混淆', status: '预检', tone: 'bg-blue-50 text-blue-700' },
  { title: '外观相似', desc: '图片、包装、造型是否需要留意', status: '重点', tone: 'bg-orange-100 text-orange-800' },
  { title: '版权素材', desc: '文案、图片素材是否建议确认', status: '预检', tone: 'bg-sky-50 text-blue-700' }
]

function sleep(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms))
}

async function waitForReport(jobId: string) {
  for (let attempt = 0; attempt < 40; attempt += 1) {
    const job = await getJobStatus(jobId)
    if (job.status === 'done') {
      currentStage.value = '报告已生成'
      progress.value = 100
      await sleep(350)
      return
    }
    if (job.status === 'failed') throw new Error('report generation failed')

    currentStage.value = job.status === 'processing' ? '正在生成报告' : '任务已提交，正在排队'
    progress.value = Math.min(94, (job.status === 'processing' ? 58 : 46) + attempt * 3)
    await sleep(1500)
  }
  throw new Error('report generation timeout')
}

async function handleSubmit() {
  if (!validation.value.isValid || isSubmitting.value) return
  isSubmitting.value = true
  currentStage.value = '正在整理资料'
  progress.value = 12
  try {
    const input = { ...formData, productLink: '', hasFile: Boolean(file.value), file: file.value ? { name: file.value.name, type: file.value.type, size: file.value.size } : undefined }
    const created = await createJob(input)
    progress.value = file.value ? 28 : 42
    currentStage.value = file.value ? '正在上传图片' : '正在启动检测'
    if (file.value) {
      await uploadJobFile(created.jobId, file.value)
      progress.value = 46
      currentStage.value = '正在启动检测'
    }
    await runJob(created.jobId)
    currentStage.value = '正在生成报告'
    progress.value = 56
    await waitForReport(created.jobId)
    await router.push(`/results/${created.jobId}`)
  } catch {
    currentStage.value = '报告生成失败，请重新提交'
  } finally {
    isSubmitting.value = false
  }
}
</script>
