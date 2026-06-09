import type { DetectionFormInput } from '@/types/domain'

const allowedImageTypes = new Set(['image/jpeg', 'image/png'])
const allowedImageExtensions = /\.(jpe?g|png)$/i
const maxImageSize = 8 * 1024 * 1024

export function validateDetectionForm(input: DetectionFormInput) {
  const errors: string[] = []
  if (!input.detectionType) errors.push('请选择检测类型')
  if (!input.brand.trim()) errors.push('请输入品牌名')
  if (!input.category) errors.push('请选择商品类目')
  if (!input.market) errors.push('请选择目标市场')
  if (!input.hasFile && !input.productLink.trim()) errors.push('请上传商品图片或输入商品链接')
  if (input.hasFile && input.file) {
    const hasAcceptedType = allowedImageTypes.has(input.file.type) || allowedImageExtensions.test(input.file.name)
    if (!hasAcceptedType) errors.push('商品图片仅支持 JPG 或 PNG')
    if (input.file.size > maxImageSize) errors.push('商品图片大小不能超过 8MB')
  }
  return { isValid: errors.length === 0, errors }
}
