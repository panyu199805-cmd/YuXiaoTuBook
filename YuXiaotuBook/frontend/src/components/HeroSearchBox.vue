<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useBookSearchSuggest } from '@/composables/useBookSearchSuggest'
import BookSearchSuggestList from '@/components/BookSearchSuggestList.vue'

defineProps<{
  tags?: { id?: number; name: string; slug?: string }[]
}>()

const router = useRouter()
const tab = ref<'books' | 'daily'>('books')
const keyword = ref('')
const booksSuggestEnabled = computed(() => tab.value === 'books')

const { suggestions, showSuggestions, activeIndex, hideSuggestions, moveActive } =
  useBookSearchSuggest(keyword, booksSuggestEnabled)

function search() {
  hideSuggestions()
  const q = keyword.value.trim()
  if (tab.value === 'daily') {
    router.push(q ? { path: '/daily', query: { q } } : '/daily')
    return
  }
  router.push(q ? { path: '/books', query: { keyword: q } } : '/books')
}

function searchTag(tag: { id?: number; name: string }) {
  hideSuggestions()
  tab.value = 'books'
  if (tag.id) {
    router.push({ path: '/books', query: { category_id: String(tag.id) } })
    return
  }
  keyword.value = tag.name
  search()
}

function pickSuggestion(id: number) {
  hideSuggestions()
  router.push(`/books/${id}`)
}

function onInputFocus() {
  if (keyword.value.trim() && suggestions.value.length) {
    showSuggestions.value = true
  }
}

function onInputBlur() {
  setTimeout(hideSuggestions, 150)
}

function onInputKeydown(e: KeyboardEvent) {
  if (!showSuggestions.value || !suggestions.value.length) return
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    moveActive(1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    moveActive(-1)
  } else if (e.key === 'Enter' && activeIndex.value >= 0) {
    e.preventDefault()
    pickSuggestion(suggestions.value[activeIndex.value].id)
  } else if (e.key === 'Escape') {
    hideSuggestions()
  }
}
</script>

<template>
  <div class="search-wrap">
    <div class="search-box">
      <div class="search-tabs">
        <button
          type="button"
          class="tab"
          :class="{ active: tab === 'books' }"
          @click="tab = 'books'"
        >
          书籍
        </button>
        <button
          type="button"
          class="tab"
          :class="{ active: tab === 'daily' }"
          @click="tab = 'daily'; hideSuggestions()"
        >
          每日读书
        </button>
      </div>

      <div class="search-row">
        <input
          v-model="keyword"
          type="search"
          :placeholder="tab === 'books' ? '搜索书名、作者，发现解读视频' : '搜索每日读书关键词'"
          autocomplete="off"
          @keyup.enter="search"
          @keydown="onInputKeydown"
          @focus="onInputFocus"
          @blur="onInputBlur"
        />
        <span class="search-divider" aria-hidden="true" />
        <button type="button" class="search-btn" aria-label="搜索" @click="search">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="7" />
            <path d="M20 20l-3-3" stroke-linecap="round" />
          </svg>
        </button>
      </div>
    </div>

    <BookSearchSuggestList
      v-if="tab === 'books' && showSuggestions && suggestions.length"
      class="suggest-dropdown"
      :items="suggestions"
      :active-index="activeIndex"
      variant="hero"
      @pick="pickSuggestion"
    />

    <div v-if="tags?.length" class="quick-tags">
      <button
        v-for="t in tags.slice(0, 8)"
        :key="t.id ?? t.name"
        type="button"
        class="tag"
        @click="searchTag(t)"
      >
        {{ t.name }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.search-wrap {
  width: min(760px, 100%);
  position: relative;
}

.search-box {
  background: rgba(255, 255, 255, 0.58);
  backdrop-filter: blur(18px) saturate(1.2);
  -webkit-backdrop-filter: blur(18px) saturate(1.2);
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: 20px;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.65);
  overflow: hidden;
}

.suggest-dropdown {
  position: absolute;
  left: 0;
  right: 0;
  top: calc(100% + 6px);
  z-index: 20;
}

.search-tabs {
  display: flex;
  gap: 28px;
  padding: 18px 24px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.tab {
  padding: 0 2px 14px;
  border: none;
  background: transparent;
  font-size: 15px;
  color: rgba(0, 0, 0, 0.45);
  cursor: pointer;
  position: relative;
  transition: color 0.2s;
}

.tab:hover {
  color: rgba(0, 0, 0, 0.72);
}

.tab.active {
  color: rgba(0, 0, 0, 0.88);
  font-weight: 500;
}

.tab.active::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: -1px;
  height: 2px;
  background: rgba(0, 0, 0, 0.88);
  border-radius: 1px;
}

.search-row {
  display: flex;
  align-items: center;
  padding: 6px 20px 8px 24px;
  gap: 12px;
  min-height: 58px;
}

.search-row input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 17px;
  padding: 14px 0;
  background: transparent;
  color: rgba(0, 0, 0, 0.88);
}

.search-row input::placeholder {
  color: rgba(0, 0, 0, 0.38);
}

.search-row input::-webkit-search-cancel-button {
  display: none;
}

.search-divider {
  width: 1px;
  height: 26px;
  background: rgba(0, 0, 0, 0.12);
  flex-shrink: 0;
}

.search-btn {
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: rgba(0, 0, 0, 0.72);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.2s, color 0.2s;
}

.search-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  color: rgba(0, 0, 0, 0.9);
}

.quick-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 6px 18px;
  margin-top: 18px;
  padding: 0 8px;
}

.tag {
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.92);
  font-size: 14px;
  padding: 4px 0;
  cursor: pointer;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.35);
  transition: opacity 0.2s;
}

.tag:hover {
  opacity: 0.85;
  text-decoration: underline;
  text-underline-offset: 3px;
}
</style>
