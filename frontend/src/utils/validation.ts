import type { DetectionFormInput } from '@/types/domain'

const allowedImageTypes = new Set(['image/jpeg', 'image/png'])
const allowedImageExtensions = /\.(jpe?g|png)$/i
const maxImageSize = 8 * 1024 * 1024

export function validateDetectionForm(input: DetectionFormInput) {
  const errors: string[] = []
  const hasText = Boolean(input.title.trim())

  if (!input.market.trim()) errors.push('请选择目标国家后再开始检测')
  if (!input.hasFile && !hasText) errors.push('请上传商品图片，或输入一段商品描述')

  if (input.hasFile && input.file) {
    const hasAcceptedType = allowedImageTypes.has(input.file.type) || allowedImageExtensions.test(input.file.name)
    if (!hasAcceptedType) errors.push('商品图片仅支持 JPG 或 PNG')
    if (input.file.size > maxImageSize) errors.push('商品图片大小不能超过 8MB')
  }

  return { isValid: errors.length === 0, errors }
}
