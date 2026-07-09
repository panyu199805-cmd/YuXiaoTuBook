/** 书籍封面占位图（由后端 /placeholders 或 Vite 代理提供） */
const BOOK_COVER_BY_ID: Record<number, string> = {
  1: '/placeholders/books/bei-tao-yan-de-yong-qi.svg',
  2: '/placeholders/books/xiao-wang-zi.svg',
  3: '/placeholders/books/fei-bao-li-gou-tong.svg',
  4: '/placeholders/books/yuan-ze.svg',
  5: '/placeholders/books/huo-zhe.svg',
  6: '/placeholders/books/zheng-mian-guan-jiao.svg',
  7: '/placeholders/books/xin-liu.svg',
  8: '/placeholders/books/jie-you-za-huo-dian.svg',
  9: '/placeholders/books/shen-du-gong-zuo.svg',
  10: '/placeholders/books/wo-men-sa.svg',
}

const FALLBACK_COLORS = [
  ['#c44536', '#e8a598'],
  ['#1b3a5f', '#4a90c2'],
  ['#6a4c93', '#c77dff'],
  ['#14213d', '#fca311'],
  ['#7f1d1d', '#b45309'],
  ['#2d6a4f', '#95d5b2'],
  ['#0077b6', '#90e0ef'],
  ['#bc6c25', '#dda15e'],
  ['#03045e', '#48cae4'],
  ['#9d8189', '#f4acb7'],
]

export function placeholderCover(id = 1): string {
  return BOOK_COVER_BY_ID[id] || `/placeholders/books/bei-tao-yan-de-yong-qi.svg`
}

/** 解析 API 返回的封面/媒体路径 */
export function resolveMediaUrl(url?: string | null, id = 1): string {
  if (!url) return placeholderCover(id)
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  return url.startsWith('/') ? url : `/${url}`
}

/** 内联 SVG，外链与静态资源均失败时的最终兜底 */
export function inlineCoverFallback(title = '宇小兔读书', id = 1): string {
  const text = title.slice(0, 8).replace(/[<>&"']/g, '')
  const [c1, c2] = FALLBACK_COLORS[((id - 1) % FALLBACK_COLORS.length + FALLBACK_COLORS.length) % FALLBACK_COLORS.length]
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="560"><defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="${c1}"/><stop offset="100%" stop-color="${c2}"/></linearGradient></defs><rect width="400" height="560" fill="url(%23g)"/><text x="200" y="280" fill="#fff" font-size="24" font-family="sans-serif" text-anchor="middle">${text}</text></svg>`
  return `data:image/svg+xml,${encodeURIComponent(svg)}`
}

const AVATAR_COLORS = [
  ['#5d87ff', '#7c3aed'],
  ['#c44536', '#e8a598'],
  ['#1b3a5f', '#4a90c2'],
  ['#2d6a4f', '#95d5b2'],
  ['#bc6c25', '#dda15e'],
]

/** 解析用户头像地址 */
export function resolveAvatarUrl(url?: string | null): string | null {
  if (!url) return null
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:')) return url
  return url.startsWith('/') ? url : `/${url}`
}

/** 无头像时按昵称首字生成默认头像 */
export function defaultAvatarImage(letter = '宇'): string {
  const ch = (letter || '宇').charAt(0).replace(/[<>&"']/g, '') || '宇'
  const [c1, c2] = AVATAR_COLORS[ch.charCodeAt(0) % AVATAR_COLORS.length]
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="${c1}"/><stop offset="100%" stop-color="${c2}"/></linearGradient></defs><rect width="64" height="64" rx="32" fill="url(%23g)"/><text x="32" y="38" fill="#fff" font-size="28" font-family="sans-serif" text-anchor="middle" font-weight="600">${ch}</text></svg>`
  return `data:image/svg+xml,${encodeURIComponent(svg)}`
}
