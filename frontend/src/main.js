// main.js (or src/main.ts)
import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js' // adjust the path if needed
import './assets/main.css'

createApp(App)
  .use(router)          // <-- critical
  .mount('#app')
