<template>
  <div class="qna-page">
    <h2>🤖 本地AI助手</h2>
    
    <div class="answer" ref="answerContainer">
      <div v-if="QAHistory.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">💬</div>
        <h3>开始你的对话</h3>
        <p>向AI助手提问，获得智能回答和建议</p>
      </div>
      
      <div v-for="(qa, index) in QAHistory" :key="index" class="qa-item">
        <div class="question-section">
          <div class="user-avatar">👤</div>
          <div class="qa-question">
            <div class="meta">{{ qa.question }}</div>
          </div>
        </div>
        
        <div class="answer-section">
          <div class="ai-avatar">🤖</div>
          <div class="bubble">
            <div class="meta">模型: {{ qa.model }}</div>
            <div v-if="loading && index === QAHistory.length - 1" class="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <!-- 流式渲染时显示原始文本，完成后显示格式化HTML -->
            <div v-if="index === currentAnswerIndex && isStreaming" class="streaming-text">
              {{ qa.answer }}
              <span class="typing-cursor" v-if="loading">|</span>
            </div>
            <div v-else v-html="getRenderedAnswer(index)" class="answer-content"></div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="input-container">
      <div class="system-prompt-area">
        <div class="input-header">
          <span class="input-label">🎯 系统提示词 (可选)</span>
          <button 
            @click="toggleSystemPrompt" 
            class="toggle-btn"
            :class="{ active: showSystemPrompt }"
          >
            {{ showSystemPrompt ? '收起' : '展开' }}
          </button>
        </div>
        <textarea 
          v-show="showSystemPrompt"
          v-model="systemPrompt" 
          placeholder="为AI提供背景信息和约束条件..." 
          class="question-input system-prompt"
        ></textarea>
      </div>
      
      <div class="input-area">
        <textarea 
          v-model="question" 
          placeholder="请输入你的问题..." 
          class="question-input"
          @keydown.enter.exact.prevent="askQuestion"
          @keydown.enter.shift.exact="handleShiftEnter"
          ref="questionTextarea"
        ></textarea>
        
        <div class="controls">
          <select v-model="selectedModel" class="model-select">
            <option v-for="model in modelList" :key="model" :value="model">{{ model }}</option>
          </select>
          
          <button 
            @click="askQuestion" 
            :disabled="loading || !question.trim()" 
            class="submit-btn"
          >
            <span v-if="loading" class="loading-spinner"></span>
            {{ loading ? '思考中...' : '发送' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Vue 响应式 API
import { ref, computed, watch, nextTick, onMounted } from 'vue'
// markdown 解析库
import { marked } from 'marked'
// 代码高亮库
import hljs from 'highlight.js'
// 代码高亮样式
import 'highlight.js/styles/github.css'
// XSS保护
import DOMPurify from 'dompurify'

// 响应式状态
const question = ref('')
const systemPrompt = ref('')
const loading = ref(false)
const selectedModel = ref('')
const modelList = ref([])
const QAHistory = ref([])
const questionTextarea = ref(null)
const answerContainer = ref(null)
const showSystemPrompt = ref(false)
const isStreaming = ref(false) // 新增：流式渲染状态
const currentAnswerIndex = ref(-1) // 新增：当前正在流式回答的索引

// SSE 事件源对象
let eventSource = null

// 配置 marked 支持代码高亮
marked.setOptions({
  highlight: function (code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true
})

// 自动调整文本域高度
function adjustTextareaHeight() {
  const textarea = questionTextarea.value
  if (textarea) {
    textarea.style.height = 'auto'
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px'
  }
}

// 监听问题输入变化，自动调整文本域高度
watch(question, () => {
  nextTick(() => {
    adjustTextareaHeight()
  })
})

// 切换系统提示词显示
function toggleSystemPrompt() {
  showSystemPrompt.value = !showSystemPrompt.value
}

// 处理Shift+Enter换行
function handleShiftEnter(event) {
  // 允许默认换行行为
  nextTick(() => {
    adjustTextareaHeight()
  })
}

// 获取最后答案
function getLastAnswer() {
  if (QAHistory.value && QAHistory.value.length === 0) {
    return ''
  }
  const qaTemp = QAHistory.value[QAHistory.value.length - 1]
  return qaTemp.answer
}

// 获取渲染答案
function getRenderedAnswer(index) {
  const qaTemp = QAHistory.value[index]
  if (!qaTemp || !qaTemp.answer) return ''
  
  // 对于当前正在流式回答的索引，直接返回原始文本以支持逐字显示
  if (index === currentAnswerIndex.value && isStreaming.value) {
    return qaTemp.answer
  }
  
  // 对于其他已完成的回答，返回格式化HTML
  const rawHtml = marked.parse(qaTemp.answer)
  const cleanHtml = DOMPurify.sanitize(rawHtml)
  return cleanHtml
}

// 自动滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (answerContainer.value) {
      answerContainer.value.scrollTop = answerContainer.value.scrollHeight
    }
  })
}

// 代码高亮函数
function highlightCodeBlocks() {
  if (answerContainer.value) {
    try {
      answerContainer.value.querySelectorAll('pre code').forEach(block => {
        if (block.textContent.trim()) {
          hljs.highlightElement(block)
        }
      })
    } catch (error) {
      console.warn('代码高亮失败:', error)
    }
  }
}

// 监听QA历史变化，自动滚动和高亮代码
watch(QAHistory, async () => {
  await nextTick()
  scrollToBottom()
  
  // 只在非流式状态下进行代码高亮
  if (!isStreaming.value) {
    highlightCodeBlocks()
  }
})

// 提交问题，流式获取答案
async function askQuestion() {
  if (!question.value.trim()) {
    // 使用现代化的提示方式替代alert
    const errorDiv = document.createElement('div')
    errorDiv.className = 'error-toast'
    errorDiv.textContent = '请输入有效的问题'
    document.body.appendChild(errorDiv)
    setTimeout(() => errorDiv.remove(), 3000)
    return
  }

  loading.value = true
  isStreaming.value = true // 开始流式渲染

  const qa = {
    question: systemPrompt.value + "\n" + question.value,
    model: selectedModel.value,
    answer: ''
  }

  QAHistory.value.push(qa)
  currentAnswerIndex.value = QAHistory.value.length - 1 // 设置当前流式回答索引

  // 清空输入框并重置高度
  question.value = ''
  adjustTextareaHeight()

  // 关闭旧的 SSE 连接
  if (eventSource) {
    eventSource.close()
  }

  try {
    // 使用 fetch 先 POST，获取流式 EventSource 通道
    const response = await fetch('/api/chat_start', {
      method: 'post',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt: qa.question,
        model: selectedModel.value
      })
    })

    if (!response.ok) throw new Error('接口请求失败')

    const streamUrl = await response.text()
    
    eventSource = new EventSource(streamUrl)
    
    eventSource.onmessage = (event) => {
      if (event.data === '[DONE]') {
        loading.value = false
        isStreaming.value = false // 结束流式渲染
        eventSource.close()
        
        // 渲染最终的格式化内容
        nextTick(() => {
          highlightCodeBlocks()
        })
        
        console.log('流式响应完成')
        return
      }
      
      try {
        const data = JSON.parse(event.data)
        if (data.text) {
          // 逐字追加文本
          QAHistory.value[currentAnswerIndex.value].answer += data.text
          console.log('接收到文本:', data.text.substring(0, 20) + '...')
          
          // 自动滚动到底部
          nextTick(() => {
            scrollToBottom()
          })
        }
      } catch (e) {
        QAHistory.value[currentAnswerIndex.value].answer += event.data
        console.log('接收到原始数据:', event.data.substring(0, 20) + '...')
        
        // 自动滚动到底部
        nextTick(() => {
          scrollToBottom()
        })
      }
    }
    
    eventSource.onerror = () => {
      loading.value = false
      isStreaming.value = false
      eventSource.close()
      QAHistory.value[currentAnswerIndex.value].answer = '连接中断，请重试。'
      console.error('SSE连接错误')
    }
    
    eventSource.addEventListener('end', () => {
      loading.value = false
      isStreaming.value = false
      eventSource.close()
      console.log('SSE流结束')
    })
    
  } catch (error) {
    loading.value = false
    isStreaming.value = false
    QAHistory.value[currentAnswerIndex.value].answer = '请求失败，请检查网络连接后重试。'
    console.error('API请求错误:', error)
  }
}

// 页面初始化时获取模型列表
onMounted(async () => {
  try {
    const res = await fetch('/api/models')
    const data = await res.json()
    modelList.value = data.models || [
      'gpt-oss:20b',
      'deepseek-r1:8b',
      'deepseek-r1:32b',
      'gemma3n:e4b',
      'llama3.1:8b',
      'llama2:latest',
      'gemma2:2b',
      'gemma3:27b'
    ]
    
    if (modelList.value.length > 0) {
      selectedModel.value = modelList.value[0]
    }
  } catch (e) {
    modelList.value = [
      'gpt-oss:20b',
      'deepseek-r1:8b',
      'deepseek-r1:32b',
      'gemma3n:e4b',
      'llama3.1:8b',
      'llama2:latest',
      'gemma2:2b',
      'gemma3:27b'
    ]
    selectedModel.value = modelList.value[0]
  }
})
</script>

<style scoped>
/* 页面整体样式，现代化设计 */
.qna-page {
  min-height: 100vh;
  width: 100%;
  box-sizing: border-box;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
  position: relative;
}

.qna-page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 20% 80%, rgba(79, 140, 255, 0.05) 0%, transparent 50%),
              radial-gradient(circle at 80% 20%, rgba(79, 140, 255, 0.05) 0%, transparent 50%);
  pointer-events: none;
}

/* 标题样式 */
h2 {
  margin: var(--spacing-xl) auto var(--spacing-lg);
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--text-primary);
  text-align: center;
  position: relative;
  padding-bottom: var(--spacing);
}

h2::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 3px;
  background: linear-gradient(90deg, var(--primary-color), var(--primary-hover));
  border-radius: 2px;
}

/* 答案区域样式 */
.answer {
  width: 90%;
  max-width: 1000px;
  flex: 1;
  margin: 0 auto var(--spacing-lg);
  font-size: var(--font-size);
  min-height: 300px;
  background: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
  padding: var(--spacing-lg);
  box-sizing: border-box;
  overflow-y: auto;
  position: relative;
  z-index: 1;
}

.answer::-webkit-scrollbar {
  width: 8px;
}

.answer::-webkit-scrollbar-track {
  background: var(--bg-secondary);
  border-radius: 4px;
}

.answer::-webkit-scrollbar-thumb {
  background: var(--gray-400);
  border-radius: 4px;
  transition: background var(--transition);
}

.answer::-webkit-scrollbar-thumb:hover {
  background: var(--gray-500);
}

/* QA项目样式 */
.qa-item {
  margin-bottom: var(--spacing-xl);
  opacity: 0;
  animation: fadeInUp 0.5s ease-out forwards;
}

.qa-item:nth-child(1) { animation-delay: 0.1s; }
.qa-item:nth-child(2) { animation-delay: 0.2s; }
.qa-item:nth-child(3) { animation-delay: 0.3s; }

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 用户信息样式 */
.qna-item p {
  margin: var(--spacing) 0 var(--spacing-sm);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  font-weight: 500;
}

.qna-item p[style*="text-align: left"] {
  padding-left: var(--spacing);
}

.qna-item p[style*="text-align: right"] {
  padding-right: var(--spacing);
}

/* 问题气泡样式 */
.qa-question {
  margin: var(--spacing-sm) 0 var(--spacing);
  max-width: 80%;
}

.qa-question .meta {
  background: linear-gradient(135deg, var(--primary-light), rgba(79, 140, 255, 0.1));
  color: var(--text-primary);
  padding: var(--spacing) var(--spacing-lg);
  border-radius: var(--border-radius-lg);
  border-bottom-left-radius: var(--border-radius-sm);
  box-shadow: var(--shadow);
  border-left: 4px solid var(--primary-color);
  position: relative;
  overflow: hidden;
  font-size: var(--font-size);
  line-height: 1.6;
  word-wrap: break-word;
}

.qa-question .meta::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: var(--primary-color);
}

/* AI回答气泡样式 */
.bubble {
  margin: var(--spacing-sm) 0 var(--spacing);
  max-width: 80%;
  margin-left: auto;
  position: relative;
}

.bubble .meta {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  margin-bottom: var(--spacing-sm);
  text-align: right;
  font-weight: 500;
}

.bubble > div:not(.meta) {
  background: linear-gradient(135deg, var(--bg-secondary), var(--bg-tertiary));
  color: var(--text-primary);
  padding: var(--spacing) var(--spacing-lg);
  border-radius: var(--border-radius-lg);
  border-bottom-right-radius: var(--border-radius-sm);
  box-shadow: var(--shadow);
  border-right: 4px solid var(--primary-color);
  position: relative;
  overflow: hidden;
  font-size: var(--font-size);
  line-height: 1.6;
  word-wrap: break-word;
  animation: typewriter 0.3s ease-out;
}

@keyframes typewriter {
  from {
    opacity: 0;
    transform: scaleX(0.9);
  }
  to {
    opacity: 1;
    transform: scaleX(1);
  }
}

/* 加载状态样式 */
.loading {
  display: inline-block;
  padding: var(--spacing-sm) var(--spacing);
  background: var(--warning-color);
  color: var(--text-white);
  border-radius: var(--border-radius);
  font-size: var(--font-size-sm);
  animation: pulse 1.5s ease-in-out infinite;
}

/* 输入区域样式 */
.input-area {
  width: 90%;
  max-width: 1000px;
  margin: 0 auto var(--spacing-xl);
  display: flex;
  gap: var(--spacing);
  align-items: flex-end;
  position: relative;
  z-index: 2;
}

.input-area:nth-of-type(2) {
  margin-bottom: var(--spacing-lg);
}

/* 输入框样式 */
.question-input {
  flex: 2;
  padding: var(--spacing);
  font-size: var(--font-size);
  border-radius: var(--border-radius-lg);
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
  resize: vertical;
  min-height: 50px;
  max-height: 200px;
  font-family: inherit;
  transition: all var(--transition);
  box-shadow: var(--shadow-sm);
}

.question-input:focus {
  border-color: var(--primary-color);
  box-shadow: var(--shadow), 0 0 0 3px rgba(79, 140, 255, 0.1);
  transform: translateY(-1px);
}

.question-input::placeholder {
  color: var(--text-muted);
  font-style: italic;
}

/* 模型选择样式 */
.model-select {
  flex: 1;
  padding: var(--spacing);
  font-size: var(--font-size);
  border-radius: var(--border-radius-lg);
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
  min-height: 50px;
  cursor: pointer;
  transition: all var(--transition);
  box-shadow: var(--shadow-sm);
}

.model-select:focus {
  border-color: var(--primary-color);
  box-shadow: var(--shadow), 0 0 0 3px rgba(79, 140, 255, 0.1);
  transform: translateY(-1px);
}

/* 按钮样式覆盖 */
.qna-page button {
  min-height: 50px;
  padding: var(--spacing) var(--spacing-lg);
  font-size: var(--font-size);
  font-weight: 600;
  border-radius: var(--border-radius-lg);
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  border: none;
  color: var(--text-white);
  cursor: pointer;
  transition: all var(--transition);
  box-shadow: var(--shadow);
  position: relative;
  overflow: hidden;
}

.qna-page button::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.qna-page button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.qna-page button:hover:not(:disabled)::before {
  width: 300px;
  height: 300px;
}

.qna-page button:active:not(:disabled) {
  transform: translateY(0);
}

.qna-page button:disabled {
  background: linear-gradient(135deg, var(--gray-300), var(--gray-400));
  color: var(--gray-600);
  cursor: not-allowed;
  transform: none;
  box-shadow: var(--shadow-sm);
}

/* Markdown内容样式优化 */
.answer :deep(pre) {
  background: var(--bg-secondary);
  border-radius: var(--border-radius);
  padding: var(--spacing);
  margin: var(--spacing) 0;
  overflow-x: auto;
  border-left: 4px solid var(--primary-color);
}

.answer :deep(code) {
  background: var(--gray-100);
  padding: 2px 6px;
  border-radius: var(--border-radius-sm);
  font-family: var(--font-mono);
  font-size: var(--font-size-sm);
}

.answer :deep(pre code) {
  background: none;
  padding: 0;
}

.answer :deep(p) {
  margin: var(--spacing) 0;
  line-height: 1.7;
}

.answer :deep(h1),
.answer :deep(h2),
.answer :deep(h3),
.answer :deep(h4),
.answer :deep(h5),
.answer :deep(h6) {
  margin: var(--spacing-lg) 0 var(--spacing);
  color: var(--text-primary);
}

.answer :deep(h1) { font-size: var(--font-size-2xl); }
.answer :deep(h2) { font-size: var(--font-size-xl); }
.answer :deep(h3) { font-size: var(--font-size-lg); }

.answer :deep(ul),
.answer :deep(ol) {
  margin: var(--spacing) 0;
  padding-left: var(--spacing-lg);
}

.answer :deep(li) {
  margin: var(--spacing-sm) 0;
  line-height: 1.6;
}

.answer :deep(blockquote) {
  border-left: 4px solid var(--primary-color);
  padding-left: var(--spacing);
  margin: var(--spacing) 0;
  font-style: italic;
  color: var(--text-secondary);
}

.answer :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: var(--spacing) 0;
}

.answer :deep(th),
.answer :deep(td) {
  border: 1px solid var(--border-color);
  padding: var(--spacing-sm);
  text-align: left;
}

.answer :deep(th) {
  background: var(--bg-secondary);
  font-weight: 600;
}

/* 输入容器样式 */
.input-container {
  width: 90%;
  max-width: 1000px;
  margin: 0 auto var(--spacing-xl);
  position: relative;
  z-index: 2;
}

/* 系统提示词区域 */
.system-prompt-area {
  margin-bottom: var(--spacing);
  background: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow);
  overflow: hidden;
  transition: all var(--transition);
}

.input-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing) var(--spacing-lg);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.input-label {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-secondary);
}

.toggle-btn {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: var(--font-size-xs);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  transition: all var(--transition);
}

.toggle-btn:hover,
.toggle-btn.active {
  background: var(--primary-color);
  color: var(--text-white);
  border-color: var(--primary-color);
}

.system-prompt {
  background: var(--bg-primary);
  font-style: italic;
  font-size: var(--font-size-sm);
}

/* 输入区域样式 */
.input-area {
  display: flex;
  gap: var(--spacing);
  align-items: flex-end;
  background: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-lg);
  transition: all var(--transition);
}

.input-area:focus-within {
  box-shadow: var(--shadow-xl), 0 0 0 2px var(--primary-color);
}

.controls {
  display: flex;
  gap: var(--spacing);
  align-items: center;
  flex-shrink: 0;
}

.submit-btn {
  position: relative;
  overflow: hidden;
  min-width: 100px;
}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: var(--spacing-sm);
}

/* 问题区域样式 */
.question-section,
.answer-section {
  display: flex;
  margin-bottom: var(--spacing-lg);
  align-items: flex-start;
  gap: var(--spacing-sm);
}

.user-avatar,
.ai-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-lg);
  flex-shrink: 0;
  box-shadow: var(--shadow);
  position: relative;
}

.user-avatar {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
}

.ai-avatar {
  background: linear-gradient(135deg, var(--success-color), #1e7e34);
}

.qa-question,
.bubble {
  flex: 1;
}

/* 流式文本样式 */
.streaming-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.6;
  font-family: inherit;
  font-size: var(--font-size);
  color: var(--text-primary);
  background: transparent;
  min-height: 1.2em;
}

.typing-cursor {
  color: var(--primary-color);
  font-weight: bold;
  animation: blink 1s infinite;
  margin-left: 2px;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* 流式内容过渡动画 */
.streaming-text {
  animation: fadeIn 0.1s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0.7; }
  to { opacity: 1; }
}
.loading-dots {
  display: flex;
  gap: 4px;
  padding: var(--spacing);
  align-items: center;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary-color);
  animation: dotPulse 1.4s ease-in-out infinite;
}

.loading-dots span:nth-child(1) { animation-delay: 0s; }
.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes dotPulse {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: var(--spacing-xxl);
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: var(--spacing);
  opacity: 0.5;
}

.empty-state h3 {
  font-size: var(--font-size-xl);
  margin-bottom: var(--spacing);
  color: var(--text-primary);
}

.empty-state p {
  font-size: var(--font-size);
  opacity: 0.7;
}

/* 错误提示样式 */
.error-toast {
  position: fixed;
  top: var(--spacing-xl);
  right: var(--spacing-xl);
  background: var(--danger-color);
  color: var(--text-white);
  padding: var(--spacing) var(--spacing-lg);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  z-index: var(--z-modal);
  animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
@media (max-width: 1024px) {
  .answer,
  .input-area {
    width: 95%;
  }
  
  h2 {
    font-size: var(--font-size-2xl);
  }
}

@media (max-width: 768px) {
  .qna-page {
    padding: var(--spacing);
  }
  
  h2 {
    font-size: var(--font-size-xl);
    margin: var(--spacing) 0 var(--spacing-lg);
  }
  
  .answer,
  .input-area {
    width: 100%;
    margin-left: 0;
    margin-right: 0;
  }
  
  .input-area {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
  
  .question-input,
  .model-select,
  .qna-page button {
    width: 100%;
  }
  
  .qa-question,
  .bubble {
    max-width: 95%;
  }
}

@media (max-width: 480px) {
  h2 {
    font-size: var(--font-size-lg);
  }
  
  .answer {
    padding: var(--spacing);
    min-height: 200px;
  }
  
  .qa-question .meta,
  .bubble > div:not(.meta) {
    padding: var(--spacing-sm) var(--spacing);
    font-size: var(--font-size-sm);
  }
}
</style>