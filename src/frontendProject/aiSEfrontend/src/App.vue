<script setup>
import { ref } from 'vue'
import QnAPage from './pages/QnAPage.vue'
import ProjectEngine from './components/ProjectEngine.vue'
import CustomProjectEngine from './components/CustomProjectEngine.vue'
import SoftwarerojectEngine from './components/SoftwareProjectEngine.vue'

const mode = ref('qna') // 默认问答模式
</script>

<template>
  <div id="app">
    <div class="mode-switch">
      <button :class="{ active: mode === 'qna' }" @click="mode = 'qna'">问答模式</button>
      <button :class="{ active: mode === 'project' }" @click="mode = 'project'">软件项目模式v1</button>
      <button :class="{ active: mode === 'customproject' }" @click="mode = 'customproject'">自定义项目模式</button>
      <button :class="{ active: mode === 'softwareproject' }" @click="mode = 'softwareproject'">软件项目模式v2</button>

    </div>
    <QnAPage v-if="mode === 'qna'" />
    <ProjectEngine v-if="mode === 'project'" />
    <CustomProjectEngine v-if="mode === 'customproject'" />
    <SoftwarerojectEngine v-if="mode === 'softwareproject'" />

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
}

.mode-switch {
  display: flex;
  gap: 16px;
  margin: 24px 0 32px 0;
  justify-content: center;
}

.mode-switch button {
  padding: 10px 28px;
  font-size: 1.1em;
  border-radius: 8px;
  border: 1px solid #4f8cff;
  background: #fff;
  color: #4f8cff;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.mode-switch button.active {
  background: #4f8cff;
  color: #fff;
}
</style>