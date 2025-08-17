// filepath: /Users/jiafei/PycharmProjects/ProjectKOTeam/src/frontendProject/aiSEfrontend/src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import QnAPage from './pages/QnAPage.vue'
import QnAv2 from './components/QnAv2.vue'
import ProjectEngine from './components/ProjectEngine.vue'
import CustomProjectEngine from './components/CustomProjectEngine.vue'
import SoftwareProjectEngine from './components/SoftwareProjectEngine.vue'

createApp(App)
  .component('QnAPage', QnAPage)
  .component('QnAv2', QnAv2)
  .component('ProjectEngine', ProjectEngine)
  .component('CustomProjectEngine', CustomProjectEngine)
  .component('SoftwareProjectEngine', SoftwareProjectEngine)
  .mount('#app')