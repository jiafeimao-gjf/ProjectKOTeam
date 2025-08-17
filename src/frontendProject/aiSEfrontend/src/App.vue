<script setup>
import { ref } from 'vue'
import QnAPage from './pages/QnAPage.vue'
import QnAv2 from './components/QnAv2.vue'
import ProjectEngine from './components/ProjectEngine.vue'
import CustomProjectEngine from './components/CustomProjectEngine.vue'
import SoftwarerojectEngine from './components/SoftwareProjectEngine.vue'

const mode = ref('qna') // 默认问答模式
</script>

<template>
  <div id="app">
    <div class="main-layout">
      <div class="mode-switch">
        <button :class="{ active: mode === 'qna' }" @click="mode = 'qna'">问答模式</button>
        <button :class="{ active: mode === 'qnav2' }" @click="mode = 'qnav2'">问答模式v2</button>
        <button :class="{ active: mode === 'project' }" @click="mode = 'project'">软件项目模式v1</button>
        <button :class="{ active: mode === 'customproject' }" @click="mode = 'customproject'">自定义项目模式</button>
        <button :class="{ active: mode === 'softwareproject' }" @click="mode = 'softwareproject'">软件项目模式v2</button>
      </div>
      
      <div class="content-area">
        <QnAPage v-if="mode === 'qna'" />
        <QnAv2 v-if="mode === 'qnav2'" />
        <ProjectEngine v-if="mode === 'project'" />
        <CustomProjectEngine v-if="mode === 'customproject'" />
        <SoftwarerojectEngine v-if="mode === 'softwareproject'" />
      </div>
    </div>
  </div>
</template>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: left;
  color: #2c3e50;
  margin: 0%;
  padding: 0%;
  height: 100vh;
}

.main-layout {
  display: flex;
  height: 100%;
}

.mode-switch {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
  width: 200px;
  background-color: #f5f7fa;
  border-right: 1px solid #e1e4e8;
}

.mode-switch button {
  padding: 12px 16px;
  font-size: 1em;
  border-radius: 8px;
  border: 1px solid #4f8cff;
  background: #fff;
  color: #4f8cff;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  text-align: left;
}

.mode-switch button.active {
  background: #4f8cff;
  color: #fff;
}

.content-area {
  flex: 1;
  padding: 24px;
  overflow: auto;
}
</style>