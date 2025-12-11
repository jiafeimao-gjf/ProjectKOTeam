// filepath: /Users/jiafei/PycharmProjects/ProjectKOTeam/src/frontendProject/aiSEfrontend/src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import QnAPage from './pages/QnAPage.vue'
import QnAv2 from './components/QnAv2.vue'
import QANew from './components/QANew.vue'

import ProjectEngine from './components/ProjectEngine.vue'
import CustomProjectEngine from './components/CustomProjectEngine.vue'
import SoftwareProjectEngine from './components/SoftwareProjectEngine.vue'
import HistoryQA from './components/HistoryQA.vue'
import ImageChat from './components/ImageChat.vue'
import CodeGen from './pages/CodeGen.vue'

createApp(App)
  .component('QnAPage', QnAPage)
  .component('QnAv2', QnAv2)
  .component('QANew', QANew)
  .component('ProjectEngine', ProjectEngine)
  .component('CustomProjectEngine', CustomProjectEngine)
  .component('SoftwareProjectEngine', SoftwareProjectEngine)
  .component('HistoryQA', HistoryQA)
  .component('ImageChat', ImageChat)
  .component('CodeGen', CodeGen)
  .mount('#app')