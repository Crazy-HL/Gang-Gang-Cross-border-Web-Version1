<template>
  <section class="rounded-[2rem] border border-slate-200/80 bg-panel/75 p-6">
    <div class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="text-sm font-bold uppercase tracking-[0.3em] text-slate-700">港港跨境AI设置</p>
        <h2 class="mt-2 text-xl font-bold text-slate-950">港港跨境AI报告配置</h2>
      </div>
      <span class="text-sm text-slate-500">用于生成港港跨境AI检测报告</span>
    </div>

    <div class="mt-6 grid gap-4 md:grid-cols-2">
      <label class="text-sm font-semibold text-slate-950">
        服务商
        <select
          v-model="form.provider"
          class="mt-2 w-full rounded-2xl border border-slate-200/80 bg-ink-2 px-4 py-3 text-slate-900"
        >
          <option value="custom">港港跨境AI自定义</option>
          <option value="openai">港港跨境AI兼容</option>
          <option value="anthropic">港港跨境AI标准</option>
        </select>
      </label>

      <label class="text-sm font-semibold text-slate-950">
        模型名称
        <input
          v-model="modelNameDisplay"
          class="mt-2 w-full rounded-2xl border border-slate-200/80 bg-ink-2 px-4 py-3 text-slate-900"
          placeholder="港港跨境AI模型名称"
        />
      </label>

      <label class="text-sm font-semibold text-slate-950">
        服务地址
        <input
          v-model="baseUrlDisplay"
          class="mt-2 w-full rounded-2xl border border-slate-200/80 bg-ink-2 px-4 py-3 text-slate-900"
          :placeholder="baseUrlPlaceholder"
        />
      </label>

      <label class="text-sm font-semibold text-slate-950">
        密钥
        <input
          v-model="form.apiKey"
          type="password"
          class="mt-2 w-full rounded-2xl border border-slate-200/80 bg-ink-2 px-4 py-3 text-slate-900"
          placeholder="保存时会覆盖旧密钥"
        />
      </label>

      <label class="text-sm font-semibold text-slate-950">
        温度
        <input
          v-model.number="form.temperature"
          type="number"
          step="0.1"
          min="0"
          max="2"
          class="mt-2 w-full rounded-2xl border border-slate-200/80 bg-ink-2 px-4 py-3 text-slate-900"
        />
      </label>

      <label class="text-sm font-semibold text-slate-950">
        最大输出
        <input
          v-model.number="form.maxTokens"
          type="number"
          min="512"
          max="8192"
          class="mt-2 w-full rounded-2xl border border-slate-200/80 bg-ink-2 px-4 py-3 text-slate-900"
        />
      </label>
    </div>

    <label class="mt-5 flex items-center gap-3 text-sm font-semibold text-slate-950">
      <input v-model="form.enabled" type="checkbox" class="h-4 w-4 accent-gold" />
      启用港港跨境AI生成报告
    </label>

    <div class="mt-6 flex items-center gap-4">
      <button
        type="button"
        :disabled="saving"
        class="rounded-full bg-gold px-5 py-3 text-sm font-bold text-white disabled:opacity-60"
        @click="save"
      >
        {{ saving ? '保存中' : '保存港港跨境AI配置' }}
      </button>
      <p v-if="message" class="text-sm text-slate-700">{{ message }}</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { getModelConfig, updateModelConfig } from '@/api/client'

const form = reactive({
  provider: 'custom',
  modelName: 'gpt-5.5',
  apiKey: '',
  baseUrl: 'https://newapi.lxhei.xyz/v1',
  temperature: 0.2,
  maxTokens: 2048,
  enabled: true,
})

const saving = ref(false)
const message = ref('')
const hideModelNameValue = ref(/gpt/i.test(form.modelName))
const hiddenBaseUrls = new Set([
  'https://newapi.lxhei.xyz/v1',
  'https://api.openai.com/v1',
  'https://api.anthropic.com/v1',
])
const hideBaseUrlValue = ref(hiddenBaseUrls.has(form.baseUrl))
const baseUrlPlaceholder = computed(() => '港港跨境AI服务地址')
const baseUrlDisplay = computed({
  get() {
    return hideBaseUrlValue.value ? '' : form.baseUrl
  },
  set(value: string) {
    hideBaseUrlValue.value = false
    form.baseUrl = value
  },
})
const modelNameDisplay = computed({
  get() {
    return hideModelNameValue.value ? '' : form.modelName
  },
  set(value: string) {
    hideModelNameValue.value = false
    form.modelName = value
  },
})

onMounted(async () => {
  const data = await getModelConfig()
  if (data.config) {
    Object.assign(form, { ...data.config, apiKey: '' })
    hideModelNameValue.value = /gpt/i.test(form.modelName)
    hideBaseUrlValue.value = hiddenBaseUrls.has(form.baseUrl)
  }
})

async function save() {
  saving.value = true
  message.value = ''
  try {
    await updateModelConfig(form)
    message.value = '港港跨境AI配置已保存'
  } catch {
    message.value = '保存失败，请检查配置'
  } finally {
    saving.value = false
  }
}
</script>
