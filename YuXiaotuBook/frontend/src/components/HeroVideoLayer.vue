<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    src?: string
    active?: boolean
    loop?: boolean
  }>(),
  {
    src: '',
    active: false,
    loop: false,
  },
)

const emit = defineEmits<{
  loadeddata: []
  ended: []
  error: []
}>()

const wrapRef = ref<HTMLElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const videoRef = ref<HTMLVideoElement | null>(null)

let rafId = 0
let resizeObs: ResizeObserver | null = null

function resizeCanvas() {
  const wrap = wrapRef.value
  const canvas = canvasRef.value
  if (!wrap || !canvas) return
  const { width, height } = wrap.getBoundingClientRect()
  const dpr = window.devicePixelRatio || 1
  canvas.width = Math.max(1, Math.floor(width * dpr))
  canvas.height = Math.max(1, Math.floor(height * dpr))
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`
  paintFrame()
}

function paintFrame() {
  const video = videoRef.value
  const canvas = canvasRef.value
  if (!video || !canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx || video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) return

  const vw = video.videoWidth
  const vh = video.videoHeight
  const cw = canvas.width
  const ch = canvas.height
  if (!vw || !vh) return

  const scale = Math.max(cw / vw, ch / vh)
  const drawW = vw * scale
  const drawH = vh * scale
  const offsetX = (cw - drawW) / 2
  const offsetY = (ch - drawH) / 2

  ctx.clearRect(0, 0, cw, ch)
  ctx.drawImage(video, offsetX, offsetY, drawW, drawH)
}

function startLoop() {
  cancelAnimationFrame(rafId)
  const tick = () => {
    paintFrame()
    const video = videoRef.value
    if (video && !video.paused && !video.ended) {
      rafId = requestAnimationFrame(tick)
    }
  }
  rafId = requestAnimationFrame(tick)
}

function stopLoop() {
  cancelAnimationFrame(rafId)
}

async function playVideo() {
  const video = videoRef.value
  if (!video) return
  try {
    await video.play()
    startLoop()
  } catch {
    /* ignore autoplay block */
  }
}

function pauseVideo() {
  videoRef.value?.pause()
  stopLoop()
}

watch(
  () => props.src,
  () => {
    stopLoop()
    videoRef.value?.load()
  },
)

watch(
  () => props.active,
  (active) => {
    if (active) void playVideo()
  },
)

onMounted(() => {
  resizeCanvas()
  resizeObs = new ResizeObserver(resizeCanvas)
  if (wrapRef.value) resizeObs.observe(wrapRef.value)
  if (props.active) void playVideo()
})

onUnmounted(() => {
  stopLoop()
  resizeObs?.disconnect()
})

defineExpose({
  get el() {
    return videoRef.value
  },
})
</script>

<template>
  <div
    ref="wrapRef"
    class="hero-video-layer"
    :class="{ 'hero-video-layer--active': active }"
  >
    <canvas ref="canvasRef" class="hero-video-canvas" aria-hidden="true" />
    <video
      ref="videoRef"
      class="hero-video-source"
      :src="src || undefined"
      :loop="loop"
      muted
      playsinline
      webkit-playsinline
      disablepictureinpicture
      disableremoteplayback
      controlslist="nodownload noremoteplayback nofullscreen"
      x-webkit-airplay="deny"
      preload="auto"
      tabindex="-1"
      aria-hidden="true"
      @loadeddata="emit('loadeddata')"
      @ended="emit('ended')"
      @error="emit('error')"
      @play="startLoop"
      @pause="stopLoop"
    />
  </div>
</template>

<style scoped>
.hero-video-layer {
  position: absolute;
  inset: 0;
  opacity: 0;
  z-index: 0;
  transition: opacity 1.2s ease-in-out;
  will-change: opacity;
  pointer-events: none;
}

.hero-video-layer--active {
  opacity: 1;
  z-index: 1;
}

.hero-video-canvas {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: brightness(1.06) saturate(1.08);
}

.hero-video-source {
  position: fixed;
  left: -9999px;
  top: -9999px;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
  visibility: hidden;
}
</style>
