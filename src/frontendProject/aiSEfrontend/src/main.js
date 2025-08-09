// filepath: /Users/jiafei/PycharmProjects/ProjectKOTeam/src/frontendProject/aiSEfrontend/src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import QnAPage from './pages/QnAPage.vue'

createApp(App)
  .component('QnAPage', QnAPage)
  .mount('#app')