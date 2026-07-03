<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  src: string
  poster?: string
  maxDuration?: number | null
}>()

const emit = defineEmits<{
  previewEnded: []
}>()

const videoRef = ref<HTMLVideoElement | null>(null)
const previewEnded = ref(false)

watch(
  () => props.src,
  () => {
    previewEnded.value = false
    if (videoRef.value) videoRef.value.load()
  }
)

function onTimeUpdate() {
  if (!props.maxDuration || previewEnded.value || !videoRef.value) return
  if (videoRef.value.currentTime >= props.maxDuration) {
    videoRef.value.pause()
    previewEnded.value = true
    emit('previewEnded')
  }
}
</script>

<template>
  <div class="video-player">
    <video
      ref="videoRef"
      :src="src"
      :poster="poster"
      controls
      playsinline
      preload="metadata"
      class="video"
      @timeupdate="onTimeUpdate"
    />
    <div v-if="previewEnded" class="preview-tip">
      试看已结束，登录后可观看完整视频
    </div>
  </div>
</template>

<style scoped>
.video-player {
  background: #000;
  border-radius: var(--radius-card);
  overflow: hidden;
  position: relative;
}
.video {
  width: 100%;
  max-height: 480px;
  display: block;
}
.preview-tip {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.75);
  color: #fff;
  text-align: center;
  padding: 12px;
  font-size: 14px;
}
</style>
