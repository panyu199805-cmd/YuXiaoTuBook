<script setup lang="ts">
import { ref } from 'vue'

const open = ref(false)

function toggle() {
  open.value = !open.value
}
</script>

<template>
  <div class="float-support">
    <transition name="panel">
      <div v-if="open" class="panel">
        <h4>在线客服</h4>
        <p class="hint">工作日 9:00 – 18:00 回复</p>
        <ul>
          <li>
            <span>客服邮箱</span>
            <a href="mailto:service@yuxiaotu.com">service@yuxiaotu.com</a>
          </li>
          <li>
            <span>会员通道</span>
            <router-link to="/member" @click="open = false">会员中心 →</router-link>
          </li>
          <li>
            <span>购书咨询</span>
            <router-link to="/books" @click="open = false">浏览书单 →</router-link>
          </li>
        </ul>
      </div>
    </transition>

    <button type="button" class="fab" aria-label="联系客服" @click="toggle">
      <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8">
        <path d="M12 2a3 3 0 0 0-3 3v1H7a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-2V5a3 3 0 0 0-3-3z" />
        <path d="M9 11h6M9 15h4" />
      </svg>
      <span>客服</span>
    </button>
  </div>
</template>

<style scoped>
.float-support {
  position: fixed;
  right: 20px;
  bottom: 28px;
  z-index: 300;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

.panel {
  width: 260px;
  background: var(--color-surface);
  border-radius: 12px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  padding: 16px 18px;
  border: 1px solid var(--color-border);
}

.panel h4 {
  font-size: 16px;
  margin-bottom: 4px;
}

.hint {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 12px;
}

.panel ul {
  list-style: none;
}

.panel li {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  padding: 8px 0;
  border-top: 1px solid var(--color-border);
  font-size: 13px;
}

.panel li span {
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.panel a {
  color: var(--color-primary);
  text-align: right;
}

.panel a:hover {
  text-decoration: underline;
}

.fab {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  width: 56px;
  height: 56px;
  border: none;
  border-radius: 12px;
  background: var(--color-surface);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  color: var(--color-text);
  cursor: pointer;
  font-size: 11px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.fab:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.16);
  color: var(--color-primary);
}

.panel-enter-active,
.panel-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}

.panel-enter-from,
.panel-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

@media (max-width: 767px) {
  .float-support {
    right: 12px;
    bottom: 16px;
  }

  .panel {
    width: min(260px, calc(100vw - 80px));
  }
}
</style>
