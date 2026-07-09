<script setup lang="ts">
import { ref, watch } from 'vue'
import type { BookSuggestItem } from '@/composables/useBookSearchSuggest'
import { inlineCoverFallback, placeholderCover, resolveMediaUrl } from '@/utils/media'

const props = defineProps<{
  items: BookSuggestItem[]
  activeIndex: number
  variant?: 'hero' | 'page'
}>()

const emit = defineEmits<{
  pick: [id: number]
}>()

const coverMap = ref<Record<number, string>>({})

function coverSrc(item: BookSuggestItem) {
  if (coverMap.value[item.id]) return coverMap.value[item.id]
  return resolveMediaUrl(item.cover, item.id)
}

function onCoverError(item: BookSuggestItem) {
  const fallback = placeholderCover(item.id)
  const current = coverMap.value[item.id] || resolveMediaUrl(item.cover, item.id)
  coverMap.value[item.id] =
    current === fallback ? inlineCoverFallback(item.title, item.id) : fallback
}

watch(
  () => props.items,
  (list) => {
    const next: Record<number, string> = {}
    for (const item of list) {
      next[item.id] = resolveMediaUrl(item.cover, item.id)
    }
    coverMap.value = next
  },
  { immediate: true },
)
</script>

<template>
  <div class="suggest-panel" :class="`suggest-panel--${variant || 'hero'}`" role="listbox">
    <div class="suggest-head">
      <span class="suggest-head-label">推荐书籍</span>
      <span class="suggest-head-count">{{ items.length }} 条匹配</span>
    </div>
    <ul class="suggest-list">
      <li
        v-for="(item, index) in items"
        :key="item.id"
        role="option"
        :aria-selected="index === activeIndex"
        class="suggest-item"
        :class="{ active: index === activeIndex }"
        @mousedown.prevent="emit('pick', item.id)"
      >
        <div class="suggest-cover">
          <img :src="coverSrc(item)" :alt="item.title" @error="onCoverError(item)" />
          <span v-if="item.has_video" class="video-dot" title="有解读视频" />
        </div>
        <div class="suggest-body">
          <div class="suggest-top">
            <h4 class="suggest-title">{{ item.title }}</h4>
            <span v-if="item.category?.name" class="suggest-cat">{{ item.category.name }}</span>
          </div>
          <p class="suggest-author">{{ item.author }}</p>
          <p v-if="item.highlight" class="suggest-highlight">「{{ item.highlight }}」</p>
          <p v-else class="suggest-highlight suggest-highlight--muted">暂无推荐语</p>
        </div>
        <span class="suggest-arrow" aria-hidden="true">→</span>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.suggest-panel {
  overflow: hidden;
  border-radius: 12px;
  animation: suggestIn 0.22s ease;
}

@keyframes suggestIn {
  from {
    opacity: 0;
    transform: translateY(-6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.suggest-panel--hero {
  background: rgba(255, 255, 255, 0.97);
  backdrop-filter: blur(20px) saturate(1.15);
  border: 1px solid rgba(255, 255, 255, 0.9);
  box-shadow:
    0 16px 48px rgba(0, 0, 0, 0.16),
    0 2px 8px rgba(0, 0, 0, 0.06);
}

.suggest-panel--page {
  background: #fff;
  border: 1px solid var(--color-border);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
}

.suggest-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 7px 12px 6px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.suggest-head-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: rgba(0, 0, 0, 0.5);
}

.suggest-head-count {
  font-size: 11px;
  color: rgba(0, 0, 0, 0.35);
}

.suggest-list {
  margin: 0;
  padding: 4px;
  list-style: none;
  max-height: 280px;
  overflow-y: auto;
}

.suggest-list::-webkit-scrollbar {
  width: 5px;
}

.suggest-list::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.12);
  border-radius: 999px;
}

.suggest-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 7px 8px;
  border-radius: 8px;
  cursor: pointer;
  transition:
    background 0.18s ease,
    box-shadow 0.18s ease;
}

.suggest-item + .suggest-item {
  margin-top: 1px;
}

.suggest-item:hover,
.suggest-item.active {
  background: linear-gradient(135deg, rgba(91, 154, 160, 0.1) 0%, rgba(201, 169, 98, 0.08) 100%);
  box-shadow: inset 2px 0 0 var(--color-primary);
}

.suggest-cover {
  position: relative;
  flex-shrink: 0;
  width: 36px;
  height: 48px;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.suggest-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-dot {
  position: absolute;
  right: 4px;
  bottom: 4px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4caf50;
  border: 1.5px solid #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

.suggest-body {
  flex: 1;
  min-width: 0;
}

.suggest-top {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 1px;
}

.suggest-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.9);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.suggest-cat {
  flex-shrink: 0;
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 999px;
  background: rgba(91, 154, 160, 0.12);
  color: var(--color-primary);
}

.suggest-author {
  margin: 0 0 2px;
  font-size: 11px;
  color: rgba(0, 0, 0, 0.42);
}

.suggest-highlight {
  margin: 0;
  font-size: 12px;
  line-height: 1.35;
  color: #8b6914;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.suggest-highlight--muted {
  color: rgba(0, 0, 0, 0.32);
  font-style: italic;
}

.suggest-arrow {
  flex-shrink: 0;
  margin-top: 2px;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.2);
  transition: color 0.18s ease;
}

.suggest-item:hover .suggest-arrow,
.suggest-item.active .suggest-arrow {
  color: var(--color-primary);
}
</style>
