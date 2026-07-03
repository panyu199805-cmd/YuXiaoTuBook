import { defineStore } from 'pinia'
import { request } from '@/api/client'
import { resolveMediaUrl } from '@/utils/media'

const preloadVideos: HTMLVideoElement[] = []

function isVideoUrl(url?: string | null) {
  return Boolean(url && /\.(mp4|webm)(\?.*)?$/i.test(url))
}

function parseBgVideos(config: Record<string, unknown> | null): string[] {
  if (!config) return []
  const list = config.bg_videos
  if (Array.isArray(list) && list.length) {
    return list.filter((item): item is string => typeof item === 'string' && isVideoUrl(item))
  }
  const single = config.bg_url
  return typeof single === 'string' && isVideoUrl(single) ? [single] : []
}

export const useSiteStore = defineStore('site', {
  state: () => ({
    config: null as Record<string, unknown> | null,
    loaded: false,
    loading: false,
  }),
  getters: {
    bgVideos: (state): string[] => parseBgVideos(state.config).map((url) => resolveMediaUrl(url)),
    useVideoBg: (state): boolean =>
      Boolean(state.config?.bg_enabled && parseBgVideos(state.config).length > 0),
  },
  actions: {
    async fetchConfig(force = false) {
      if (this.loaded && !force) return this.config
      if (this.loading) return this.config
      this.loading = true
      try {
        const res = await request<Record<string, unknown>>({ url: '/site/config' })
        if (res.code === 200 && res.data) {
          this.config = res.data
          this.preloadBackground()
        }
        this.loaded = true
        return this.config
      } catch {
        this.loaded = true
        return this.config
      } finally {
        this.loading = false
      }
    },
    preloadBackground() {
      const urls = this.bgVideos
      if (!urls.length) return

      urls.forEach((url, index) => {
        let video = preloadVideos[index]
        if (!video) {
          video = document.createElement('video')
          video.preload = 'auto'
          video.muted = true
          video.playsInline = true
          video.setAttribute('webkit-playsinline', 'true')
          preloadVideos[index] = video
        }
        const absolute = new URL(url, window.location.origin).href
        if (video.src !== absolute) {
          video.src = url
          video.load()
        }
        if (index === 0) void video.play().catch(() => {})
      })
    },
  },
})
