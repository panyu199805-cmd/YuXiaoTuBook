export type VideoFitMode = 'cover' | 'contain'

export function drawVideoToCanvas(
  video: HTMLVideoElement,
  canvas: HTMLCanvasElement,
  fit: VideoFitMode = 'cover',
) {
  const ctx = canvas.getContext('2d')
  if (!ctx || video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) return false

  const width = canvas.clientWidth
  const height = canvas.clientHeight
  if (!width || !height) return false

  if (canvas.width !== width || canvas.height !== height) {
    canvas.width = width
    canvas.height = height
  }

  const vw = video.videoWidth
  const vh = video.videoHeight
  if (!vw || !vh) return false

  const scale = fit === 'cover'
    ? Math.max(width / vw, height / vh)
    : Math.min(width / vw, height / vh)
  const drawWidth = vw * scale
  const drawHeight = vh * scale
  const offsetX = (width - drawWidth) / 2
  const offsetY = (height - drawHeight) / 2

  ctx.clearRect(0, 0, width, height)
  if (fit === 'contain') {
    ctx.fillStyle = '#000'
    ctx.fillRect(0, 0, width, height)
  }
  ctx.drawImage(video, offsetX, offsetY, drawWidth, drawHeight)
  return true
}

export function createVideoRenderLoop(draw: () => void) {
  let frameId: number | null = null

  return {
    start() {
      if (frameId !== null) return
      const loop = () => {
        draw()
        frameId = requestAnimationFrame(loop)
      }
      frameId = requestAnimationFrame(loop)
    },
    stop() {
      if (frameId === null) return
      cancelAnimationFrame(frameId)
      frameId = null
    },
  }
}

export function formatVideoTime(seconds: number) {
  if (!Number.isFinite(seconds) || seconds < 0) return '0:00'
  const total = Math.floor(seconds)
  const mins = Math.floor(total / 60)
  const secs = total % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
