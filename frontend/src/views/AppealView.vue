<template>
  <SiteHeader />
  <main class="bg-[linear-gradient(135deg,#ffffff_0%,#eef7ff_52%,#fff8ed_100%)] px-5 py-12 lg:px-8 lg:py-16">
    <div class="mx-auto max-w-7xl">
      <section class="grid gap-8 lg:grid-cols-[0.95fr_1.05fr] lg:items-start">
        <div>
          <p class="inline-flex rounded-full border border-blue-200 bg-white/80 px-4 py-2 text-sm font-bold text-blue-700 shadow-sm shadow-blue-900/5">
            平台侵权申诉处理
          </p>
          <h1 class="mt-6 max-w-3xl text-4xl font-black leading-tight text-slate-950 md:text-6xl">
            商品下架、店铺受限，先把申诉资料理清楚
          </h1>
          <p class="mt-5 max-w-2xl text-base leading-7 text-slate-600">
            面向亚马逊、Temu、TikTok Shop、eBay、速卖通等平台，整理投诉原因、申诉材料和下一步处理路径。
          </p>

          <div class="mt-8 grid gap-3 sm:grid-cols-3">
            <div v-for="item in servicePoints" :key="item.title" class="rounded-2xl border border-white/80 bg-white/75 p-4 shadow-sm shadow-blue-900/5">
              <p class="text-sm font-black text-slate-950">{{ item.title }}</p>
              <p class="mt-2 text-xs font-bold leading-5 text-slate-500">{{ item.desc }}</p>
            </div>
          </div>
        </div>

        <form class="rounded-[2rem] border border-white/80 bg-white/88 p-5 shadow-2xl shadow-blue-900/12 backdrop-blur md:p-7" @submit.prevent="handleSubmit">
          <div class="rounded-[1.75rem] border border-blue-100 bg-[linear-gradient(145deg,#ffffff_0%,#f3f9ff_62%,#fff7ed_100%)] p-5">
            <p class="text-sm font-bold text-blue-700">提交申诉资料</p>
            <h2 class="mt-2 text-2xl font-black text-slate-950">平台申诉初步评估</h2>
          </div>

          <div class="mt-5 grid gap-4 md:grid-cols-2">
            <label class="block text-sm font-black text-slate-950">
              涉及平台
              <select v-model="form.platform" class="mt-3 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-bold text-slate-900 outline-none transition focus:border-blue-300 focus:bg-white focus:ring-4 focus:ring-blue-100" aria-label="涉及平台">
                <option value="">请选择平台</option>
                <option v-for="item in platforms" :key="item" :value="item">{{ item }}</option>
              </select>
            </label>

            <label class="block text-sm font-black text-slate-950">
              问题类型
              <select v-model="form.issueType" class="mt-3 w-full rounded-2xl border border-orange-100 bg-orange-50 px-4 py-3 text-sm font-bold text-orange-900 outline-none transition focus:border-orange-300 focus:bg-white focus:ring-4 focus:ring-orange-100" aria-label="问题类型">
                <option value="">请选择问题类型</option>
                <option v-for="item in issueTypes" :key="item" :value="item">{{ item }}</option>
              </select>
            </label>
          </div>

          <div class="mt-5 grid gap-4 md:grid-cols-2">
            <label class="block text-sm font-black text-slate-950">
              店铺名称
              <input v-model="form.storeName" class="mt-3 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-bold text-slate-900 outline-none transition focus:border-blue-300 focus:bg-white focus:ring-4 focus:ring-blue-100" placeholder="填写店铺名称" />
            </label>

            <label class="block text-sm font-black text-slate-950">
              联系方式
              <input v-model="form.contact" class="mt-3 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-bold text-slate-900 outline-none transition focus:border-blue-300 focus:bg-white focus:ring-4 focus:ring-blue-100" placeholder="手机号或微信" />
            </label>
          </div>

          <label class="mt-5 block text-sm font-black text-slate-950">
            商品链接或投诉编号
            <input v-model="form.reference" class="mt-3 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-bold text-slate-900 outline-none transition focus:border-blue-300 focus:bg-white focus:ring-4 focus:ring-blue-100" placeholder="商品链接、ASIN、Case ID 或投诉编号" />
          </label>

          <label class="mt-5 block text-sm font-black text-slate-950">
            情况说明
            <textarea v-model="form.description" rows="5" class="mt-3 w-full resize-none rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-300 focus:bg-white focus:ring-4 focus:ring-blue-100" placeholder="描述平台通知、权利人投诉、商品下架或店铺受限情况" />
          </label>

          <label for="appeal-files" class="mt-5 block cursor-pointer rounded-[1.5rem] border border-dashed border-blue-200 bg-blue-50/75 p-4 text-center transition hover:border-blue-300 hover:bg-blue-50">
            <span class="block text-sm font-black text-slate-950">{{ selectedFileLabel }}</span>
            <span class="mt-1 block text-xs font-bold text-slate-500">平台通知截图、邮件、Listing 截图或权利人投诉材料</span>
          </label>
          <input id="appeal-files" type="file" multiple class="sr-only" @change="handleFiles" />

          <p v-if="message" class="mt-5 rounded-2xl border px-4 py-3 text-sm font-bold" :class="messageTone">
            {{ message }}
          </p>
          <div v-if="isSubmitting" class="mt-5 rounded-2xl border border-blue-100 bg-blue-50 p-4">
            <div class="flex items-center justify-between gap-3">
              <span class="text-sm font-black text-blue-700">正在生成初步建议报告</span>
              <span class="text-xs font-bold text-slate-500">港港跨境AI 分析可能需要约 1 分钟</span>
            </div>
            <div class="mt-3 h-2.5 overflow-hidden rounded-full bg-white">
              <div class="h-full w-2/3 rounded-full bg-[linear-gradient(90deg,#2563eb_0%,#38bdf8_58%,#fb923c_100%)]" />
            </div>
          </div>

          <button type="submit" :disabled="isSubmitting" class="mt-5 w-full rounded-full bg-gold px-8 py-4 text-sm font-black text-white shadow-glow transition hover:bg-blue-600 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-500 disabled:shadow-none">
            {{ isSubmitting ? '正在生成建议报告' : '提交并生成建议报告' }}
          </button>
        </form>
      </section>

      <section v-if="adviceReport" ref="reportSection" class="mt-10 rounded-[2rem] border border-white/80 bg-white/88 p-5 shadow-2xl shadow-blue-900/12 md:p-7">
        <div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <p class="flex flex-wrap items-center gap-2 text-sm font-black text-blue-700">
              初步建议报告
              <span class="rounded-full border px-3 py-1 text-xs" :class="sourceClass(adviceReport.source)">
                {{ sourceLabels[adviceReport.source ?? 'fallback'] }}
              </span>
            </p>
            <h2 class="mt-2 text-3xl font-black text-slate-950">{{ adviceReport.title }}</h2>
            <p class="mt-3 max-w-4xl text-sm leading-7 text-slate-600">{{ adviceReport.summary }}</p>
          </div>
          <span class="w-fit rounded-full px-4 py-2 text-sm font-black" :class="riskClass(adviceReport.riskLevel)">
            {{ riskLabels[adviceReport.riskLevel] }}
          </span>
        </div>

        <div class="mt-6 grid gap-4 lg:grid-cols-3">
          <div v-for="section in adviceReport.sections" :key="section.title" class="rounded-2xl border border-blue-100 bg-[linear-gradient(145deg,#ffffff_0%,#f8fbff_68%,#fff7ed_100%)] p-5">
            <h3 class="text-base font-black text-slate-950">{{ section.title }}</h3>
            <ul class="mt-3 space-y-2 text-sm leading-6 text-slate-600">
              <li v-for="item in section.items" :key="item">· {{ item }}</li>
            </ul>
          </div>
        </div>

        <div class="mt-6 grid gap-4 lg:grid-cols-[1fr_0.42fr]">
          <div class="rounded-2xl border border-slate-200/80 bg-white p-5">
            <h3 class="text-base font-black text-slate-950">下一步行动</h3>
            <ol class="mt-3 space-y-2 text-sm leading-6 text-slate-600">
              <li v-for="(item, index) in adviceReport.nextActions" :key="item">{{ index + 1 }}. {{ item }}</li>
            </ol>
          </div>
          <div class="rounded-2xl border border-orange-200 bg-orange-50 p-5">
            <p class="text-xs font-black text-orange-800">需要服务支持</p>
            <h3 class="mt-2 text-xl font-black text-slate-950">联系我们继续处理</h3>
            <p class="mt-2 text-sm leading-6 text-slate-600">{{ adviceReport.contactHint }}</p>
            <button type="button" class="mt-4 inline-flex rounded-full bg-gold px-5 py-3 text-sm font-black text-white shadow-glow transition hover:bg-blue-600" @click="showContact = true">
              联系港港跨境
            </button>
          </div>
        </div>
      </section>

      <section class="mt-10 grid gap-4 md:grid-cols-4">
        <div v-for="step in steps" :key="step.title" class="rounded-2xl border border-white/80 bg-white/75 p-5 shadow-sm shadow-blue-900/5">
          <p class="text-xs font-black text-blue-700">{{ step.index }}</p>
          <h3 class="mt-2 text-base font-black text-slate-950">{{ step.title }}</h3>
          <p class="mt-2 text-sm leading-6 text-slate-600">{{ step.desc }}</p>
        </div>
      </section>
    </div>
  </main>
  <ContactQrModal :open="showContact" @close="showContact = false" />
  <SiteFooter />
</template>

<script setup lang="ts">
import { computed, nextTick, reactive, ref } from 'vue'
import SiteHeader from '@/components/site/SiteHeader.vue'
import SiteFooter from '@/components/site/SiteFooter.vue'
import ContactQrModal from '@/components/common/ContactQrModal.vue'
import { createServiceRequest } from '@/api/client'
import type { ServiceAdviceReport } from '@/types/domain'

const platforms = ['亚马逊', 'Temu', 'TikTok Shop', 'eBay', '速卖通', 'SHEIN', '独立站', '其他']
const issueTypes = ['商品下架', '店铺受限', '资金冻结', '品牌投诉', '图片侵权', '商标侵权', '版权侵权', '其他']
const servicePoints = [
  { title: '平台通知梳理', desc: '识别投诉类型、权利人信息和平台处理节点。' },
  { title: '申诉材料清单', desc: '整理授权、采购、设计来源和整改说明。' },
  { title: '处理路径建议', desc: '区分申诉、整改、补材料和协商方案。' }
]
const steps = [
  { index: '01', title: '提交资料', desc: '上传平台通知和商品信息。' },
  { index: '02', title: '初步评估', desc: '判断投诉类型和关键缺口。' },
  { index: '03', title: '整理方案', desc: '形成申诉思路和补充材料清单。' },
  { index: '04', title: '跟进处理', desc: '根据平台反馈继续调整。' }
]

const form = reactive({ platform: '', issueType: '', storeName: '', contact: '', reference: '', description: '' })
const fileNames = ref<string[]>([])
const message = ref('')
const messageTone = ref('border-blue-100 bg-blue-50 text-blue-700')
const isSubmitting = ref(false)
const adviceReport = ref<ServiceAdviceReport | null>(null)
const reportSection = ref<HTMLElement | null>(null)
const showContact = ref(false)
const selectedFileLabel = computed(() => fileNames.value.length ? `已选择 ${fileNames.value.length} 个文件` : '上传申诉相关文件')
const riskLabels = { high: '高风险', medium: '中风险', low: '低风险' }
const sourceLabels = { model: '港港跨境AI', fallback: '港港跨境基础评估' }

function handleFiles(event: Event) {
  fileNames.value = Array.from((event.target as HTMLInputElement).files ?? []).map((file) => file.name)
}

function validateContact(contact: string) {
  const value = contact.trim()
  if (!value) return '请填写联系方式'
  if (/^\d+$/.test(value) && !/^1\d{10}$/.test(value)) return '手机号需为 11 位，并以 1 开头'
  if (!/^1\d{10}$/.test(value) && !/^[A-Za-z][-_A-Za-z0-9]{5,19}$/.test(value)) return '请填写完整手机号，或填写 6-20 位微信号'
  return ''
}

async function handleSubmit() {
  if (isSubmitting.value) return
  if (!form.platform || !form.issueType || !form.contact) {
    message.value = '请先填写平台、问题类型和联系方式。'
    messageTone.value = 'border-orange-200 bg-orange-50 text-orange-800'
    return
  }
  const contactError = validateContact(form.contact)
  if (contactError) {
    message.value = contactError
    messageTone.value = 'border-orange-200 bg-orange-50 text-orange-800'
    return
  }

  isSubmitting.value = true
  adviceReport.value = null
  try {
    const result = await createServiceRequest({
      requestType: 'appeal',
      platform: form.platform,
      contact: form.contact,
      title: `${form.platform}${form.issueType}申诉`,
      issueType: form.issueType,
      storeName: form.storeName,
      reference: form.reference,
      description: form.description,
      fileNames: fileNames.value,
    })
    adviceReport.value = result.adviceReport
    message.value = `已生成服务工单 ${result.request.id}，建议报告如下。`
    messageTone.value = 'border-blue-100 bg-blue-50 text-blue-700'
    await nextTick()
    reportSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  } catch (error) {
    message.value = error instanceof Error ? error.message : '提交失败，请稍后再试。'
    messageTone.value = 'border-orange-200 bg-orange-50 text-orange-800'
  } finally {
    isSubmitting.value = false
  }
}

function riskClass(level: ServiceAdviceReport['riskLevel']) {
  if (level === 'high') return 'bg-orange-100 text-orange-800'
  if (level === 'medium') return 'bg-amber-100 text-amber-800'
  return 'bg-blue-50 text-blue-700'
}

function sourceClass(source?: ServiceAdviceReport['source']) {
  return source === 'model' ? 'border-blue-200 bg-blue-50 text-blue-700' : 'border-orange-200 bg-orange-50 text-orange-800'
}
</script>
