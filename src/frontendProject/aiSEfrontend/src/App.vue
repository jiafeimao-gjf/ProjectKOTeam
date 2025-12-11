<script setup>
import { ref } from 'vue'
import QnAPage from './pages/QnAPage.vue'
import QnAv2 from './components/QnAv2.vue'
import QANew from './components/QANew.vue'
import ProjectEngine from './components/ProjectEngine.vue'
import CustomProjectEngine from './components/CustomProjectEngine.vue'
import SoftwareProjectEngine from './components/SoftwareProjectEngine.vue'
import HistoryQA from './components/HistoryQA.vue'
import ImageChat from './components/ImageChat.vue'
import CodeGen from './pages/CodeGen.vue'

const mode = ref('qna') // 默认问答模式
</script>

<template>
  <div id="app">
    <div class="main-layout">
      <div class="mode-switch">
        <!-- 对话模式分组 -->
        <div class="mode-group">
          <div class="mode-group-title">对话模式</div>
          <button :class="{ active: mode === 'qna' }" @click="mode = 'qna'">💬 问答模式</button>
          <button :class="{ active: mode === 'qaNew' }" @click="mode = 'qaNew'">💬 问答模式-新UI</button>

          <button :class="{ active: mode === 'qnav2' }" @click="mode = 'qnav2'">🚀 问答模式v2</button>
          <button :class="{ active: mode === 'history' }" @click="mode = 'history'">📚 历史问答</button>
        </div>

        <!-- 项目模式分组 -->
        <div class="mode-group">
          <div class="mode-group-title">项目模式</div>
          <button :class="{ active: mode === 'project' }" @click="mode = 'project'">🏗️ 软件项目v1</button>
          <button :class="{ active: mode === 'softwareproject' }" @click="mode = 'softwareproject'">⚡ 软件项目v2</button>
          <button :class="{ active: mode === 'customproject' }" @click="mode = 'customproject'">🎯 自定义项目</button>
        </div>

        <!-- 其他模式分组 -->
        <div class="mode-group">
          <div class="mode-group-title">其他功能</div>
          <button :class="{ active: mode === 'codegen' }" @click="mode = 'codegen'">📝 代码生成</button>
          <button :class="{ active: mode === 'imagechat' }" @click="mode = 'imagechat'">🖼️ 图片对话</button>
        </div>
      </div>

      <div class="content-area">
        <QnAPage v-if="mode === 'qna'" class="fade-in" />
        <QANew v-if="mode === 'qaNew'" class="fade-in" />
        <QnAv2 v-if="mode === 'qnav2'" class="fade-in" />
        <ProjectEngine v-if="mode === 'project'" class="fade-in" />
        <CustomProjectEngine v-if="mode === 'customproject'" class="fade-in" />
        <SoftwareProjectEngine v-if="mode === 'softwareproject'" class="fade-in" />
        <HistoryQA v-if="mode === 'history'" class="fade-in" />
        <ImageChat v-if="mode === 'imagechat'" class="fade-in" />
        <CodeGen v-if="mode === 'codegen'" class="fade-in" />
      </div>
    </div>
  </div>
</template>

<style scoped>
#app {
  font-family: var(--font-family);
  color: var(--text-primary);
  height: 100vh;
  background-color: var(--bg-secondary);
}

.main-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  border: 1px solid var(--border-dark);
  box-sizing: border-box;
}

.mode-switch {
  display: flex;
  flex-direction: column;
  gap: var(--spacing);
  padding: var(--spacing-lg);
  width: 240px;
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  border-right: 2px solid var(--border-medium);
  box-shadow: var(--shadow);
  overflow-y: auto;
  position: relative;
}

.mode-switch::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 2px;
  height: 100%;
  background: linear-gradient(to bottom, 
    transparent, 
    var(--border-medium) 5%, 
    var(--border-medium) 95%, 
    transparent
  );
}

.mode-switch::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 1px;
  background: var(--border-medium);
}

.mode-switch button {
  padding: var(--spacing-sm) var(--spacing);
  font-size: var(--font-size-sm);
  border-radius: var(--border-radius);
  border: 2px solid var(--border-medium);
  background: var(--bg-primary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition);
  text-align: left;
  position: relative;
  overflow: hidden;
  font-weight: 500;
  box-shadow: var(--shadow-sm);
  position: relative;
}

.mode-switch button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s;
}

.mode-switch button:hover {
  background: var(--primary-light);
  color: var(--primary-color);
  transform: translateX(4px);
  box-shadow: var(--shadow);
  border-color: var(--primary-color);
}

.mode-switch button:hover::before {
  left: 100%;
}

.mode-switch button.active {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
  color: var(--text-white);
  border-color: var(--primary-color);
  box-shadow: var(--shadow);
  font-weight: 600;
}

.mode-switch button.active::after {
  content: '✓';
  position: absolute;
  right: var(--spacing);
  top: 50%;
  transform: translateY(-50%);
  font-size: var(--font-size-sm);
}

/* 模式分组样式 */
.mode-switch .mode-group {
  margin-bottom: var(--spacing-lg);
}

.mode-switch .mode-group-title {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--spacing-sm);
  font-weight: 600;
  padding-bottom: 10px;
  padding-top: 10px;
}

.content-area {
  flex: 1;
  padding: 0;
  overflow: hidden;
  height: 100%;
  background: var(--bg-secondary);
  position: relative;
  border-left: 1px solid var(--border-light);
}

.content-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(to right, 
    var(--border-medium), 
    var(--border-dark) 20%, 
    var(--border-dark) 80%, 
    var(--border-medium)
  );
}

.content-area::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border: 1px solid var(--border-light);
  border-top: none;
  pointer-events: none;
}

/* 确保所有子组件都能自适应显示 */
.content-area > div {
  height: 100%;
  width: 100%;
  overflow: hidden;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .mode-switch {
    width: 200px;
    padding: var(--spacing);
  }
  
  .mode-switch button {
    font-size: var(--font-size-xs);
    padding: var(--spacing) var(--spacing-sm);
  }
}

@media (max-width: 768px) {
  .main-layout {
    flex-direction: column;
  }
  
  .mode-switch {
    width: 100%;
    height: auto;
    flex-direction: row;
    padding: var(--spacing) var(--spacing-lg);
    border-right: none;
    border-bottom: 1px solid var(--border-color);
    overflow-x: auto;
    overflow-y: hidden;
    gap: var(--spacing-sm);
  }
  
  .mode-switch button {
    flex-shrink: 0;
    white-space: nowrap;
    font-size: var(--font-size-xs);
    padding: var(--spacing-sm) var(--spacing);
  }
  
  .content-area {
    flex: 1;
    height: calc(100vh - 80px);
  }
}

@media (max-width: 480px) {
  .mode-switch {
    padding: var(--spacing-sm);
    gap: var(--spacing-xs);
  }
  
  .mode-switch button {
    font-size: 10px;
    padding: 6px 8px;
  }
}

/* 滚动条样式 */
.mode-switch::-webkit-scrollbar {
  width: 6px;
}

.mode-switch::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}

.mode-switch::-webkit-scrollbar-thumb {
  background: var(--gray-400);
  border-radius: 3px;
}

.mode-switch::-webkit-scrollbar-thumb:hover {
  background: var(--gray-500);
}

/* 动画效果 */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.content-area > div {
  animation: slideIn 0.3s ease-out;
}
</style>