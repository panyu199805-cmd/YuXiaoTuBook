<script setup lang="ts">
import { ref, watch } from 'vue'
import { inlineCoverFallback, placeholderCover, resolveMediaUrl } from '@/utils/media'

const props = defineProps<{
  id: number
  title: string
  author: string
  cover: string
  category?: { name: string }
  has_video?: boolean
  price?: number
}>()

const displayCover = ref(resolveMediaUrl(props.cover, props.id))

watch(
  () => [props.cover, props.id] as const,
  ([cover, id]) => {
    displayCover.value = resolveMediaUrl(cover, id)
  },
)

function onCoverError() {
  const fallback = placeholderCover(props.id)
  displayCover.value =
    displayCover.value === fallback ? inlineCoverFallback(props.title, props.id) : fallback
}
</script>

<template>
  <router-link :to="`/books/${id}`" class="book-card">
    <div class="cover-wrap">
      <img :src="displayCover" :alt="title" loading="lazy" @error="onCoverError" />
      <span v-if="has_video === false" class="badge">解读筹备中</span>
    </div>
    <div class="info">
      <h3>{{ title }}</h3>
      <p class="meta">{{ author }} · {{ category?.name }}</p>
      <p v-if="price" class="price">¥{{ price.toFixed(2) }}</p>
    </div>
  </router-link>
</template>

<style scoped>
.book-card {
  display: block;
  background: var(--color-surface);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
  overflow: hidden;
  transition: transform 0.25s, box-shadow 0.25s;
}
.book-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}
.cover-wrap {
  position: relative;
  aspect-ratio: 3/4;
  overflow: hidden;
}
.cover-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
}
.info {
  padding: 12px 14px 16px;
}
.info h3 {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.meta {
  font-size: 13px;
  color: var(--color-text-secondary);
}
.price {
  margin-top: 6px;
  color: var(--color-primary);
  font-weight: 600;
}
</style>
