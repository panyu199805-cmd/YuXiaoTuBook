import { ref, watch, type Ref } from 'vue'
import { request } from '@/api/client'

export interface BookSuggestItem {
  id: number
  title: string
  author: string
  cover?: string
  highlight?: string | null
  category?: { id?: number; name: string } | null
  has_video?: boolean
}

export function useBookSearchSuggest(keyword: Ref<string>, enabled: Ref<boolean>) {
  const suggestions = ref<BookSuggestItem[]>([])
  const showSuggestions = ref(false)
  const activeIndex = ref(-1)
  let timer: ReturnType<typeof setTimeout> | null = null
  let requestId = 0

  async function fetchSuggestions(q: string) {
    const trimmed = q.trim()
    if (!trimmed) {
      suggestions.value = []
      showSuggestions.value = false
      return
    }

    const currentId = ++requestId
    const res = await request<{ list: BookSuggestItem[] }>({
      url: '/books',
      params: { keyword: trimmed, page: 1, page_size: 8 },
    })
    if (currentId !== requestId) return

    if (res.code === 200) {
      suggestions.value = res.data?.list || []
      showSuggestions.value = suggestions.value.length > 0
      activeIndex.value = -1
    }
  }

  watch(
    [keyword, enabled],
    () => {
      if (timer) clearTimeout(timer)
      if (!enabled.value) {
        suggestions.value = []
        showSuggestions.value = false
        return
      }
      const q = keyword.value.trim()
      if (q.length < 1) {
        suggestions.value = []
        showSuggestions.value = false
        return
      }
      timer = setTimeout(() => {
        void fetchSuggestions(q)
      }, 280)
    },
    { flush: 'post' },
  )

  function hideSuggestions() {
    showSuggestions.value = false
    activeIndex.value = -1
  }

  function moveActive(delta: number) {
    if (!suggestions.value.length) return
    const len = suggestions.value.length
    if (activeIndex.value < 0) {
      activeIndex.value = delta > 0 ? 0 : len - 1
      return
    }
    activeIndex.value = (activeIndex.value + delta + len) % len
  }

  return {
    suggestions,
    showSuggestions,
    activeIndex,
    hideSuggestions,
    moveActive,
  }
}
