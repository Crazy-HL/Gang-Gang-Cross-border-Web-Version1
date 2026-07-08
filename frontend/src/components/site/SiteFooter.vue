<template>
  <footer class="no-print border-t border-slate-200/80 bg-white">
    <div class="mx-auto grid max-w-7xl gap-8 px-5 py-10 md:grid-cols-[1.5fr_1fr_1fr] lg:px-8">
      <div>
        <div class="text-lg font-bold text-slate-950">港港跨境 IP 风险检测</div>
        <p class="mt-3 max-w-xl text-sm leading-6 text-slate-500">
          为跨境卖家、品牌方和供应链团队提供商标、外观、版权风险预警，帮助团队在上架和投放前降低知识产权损失。
        </p>
      </div>
      <div>
        <div class="text-sm font-semibold text-slate-700">产品入口</div>
        <div class="mt-3 flex flex-col gap-2 text-sm text-slate-500">
          <RouterLink to="/detect" class="hover:text-blue-700">上传检测</RouterLink>
          <RouterLink to="/appeal" class="hover:text-blue-700">平台申诉</RouterLink>
          <RouterLink to="/tro-settlement" class="hover:text-blue-700">TRO 和解</RouterLink>
          <RouterLink to="/dashboard" class="hover:text-blue-700">我的任务</RouterLink>
          <RouterLink to="/dashboard?tab=reports" class="hover:text-blue-700">我的报告</RouterLink>
        </div>
      </div>
      <div>
        <div class="text-sm font-semibold text-slate-700">联系方式</div>
        <p class="mt-3 text-sm leading-6 text-slate-500">
          手机号：15811116302<br />
          服务时间：周一至周五 09:00-18:00
        </p>
      </div>
    </div>
  </footer>
</template>
