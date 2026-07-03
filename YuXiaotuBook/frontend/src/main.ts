import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import 'element-plus/dist/index.css'
import { createHead } from '@unhead/vue'
import App from './App.vue'
import router from './router'
import { useSiteStore } from './stores/site'
import './styles/variables.css'
import './styles/global.css'
import './styles/admin-theme.css'

const app = createApp(App)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
void useSiteStore().fetchConfig()
app.use(router)
app.use(ElementPlus, { locale: zhCn })
app.use(createHead())
app.mount('#app')
