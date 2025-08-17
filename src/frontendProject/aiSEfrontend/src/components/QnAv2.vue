<template>
  <div class="qna-page">
    <h3>本地双agent助手对话助手</h3>
    <div class="answer" id="md">
      <!-- 加载中提示 -->
      <span v-if="loading">正在生成对话...</span>
      <!-- 渲染消息列表（Markdown） -->
      <div v-for="(msg, idx) in messages" :key="idx"
        :class="['message-item', msg.speaker === 'Agent1' ? 'agent1' : 'agent2']">
        <div class="meta"><strong>{{ msg.speaker }}</strong></div>
        <div class="bubble" v-html="renderMarkdown(msg.text)"></div>
      </div>
    </div>
    <div class="bottom-bar">
      <div class="bar-row">
        <div class="input-area">
          <p>模型1角色预设:</p>
          <!-- 问题输入框 -->
          <input v-model="question" placeholder="输入预设内容..." />
          <!-- 模型选择下拉框，始终可见所有模型 -->
          <select v-model="selectedModel" class="model-select">
            <option v-for="model in modelList" :key="model" :value="model">{{ model }}</option>
          </select>
        </div>
      </div>
      <div class="bar-row">
        <div class="input-area">
          <p>模型2角色预设:</p>
          <!-- 问题输入框 -->
          <input v-model="question2" placeholder="输入预设内容..." />
          <!-- 模型选择下拉框，始终可见所有模型 -->
          <select v-model="selectedModel2" class="model-select">
            <option v-for="model in modelList" :key="model" :value="model">{{ model }}</option>
          </select>
        </div>
      </div>
      <div class="bar-row">
        <div class="input-area">
          <label style="display:flex;align-items:center;gap:8px;">
            <input type="checkbox" v-model="model3Enabled" /> 启用模型3
          </label>
          <p style="margin-left:6px">模型3角色预设:</p>
          <!-- 问题输入框 -->
          <input v-model="question3" :disabled="!model3Enabled" placeholder="输入预设内容..." />
          <!-- 模型选择下拉框，始终可见所有模型 -->
          <select v-model="selectedModel3" class="model-select" :disabled="!model3Enabled">
            <option v-for="model in modelList" :key="model" :value="model">{{ model }}</option>
          </select>
        </div>
      </div>
      <div class="bar-row control-row">
        <div class="control-group">
          <label style="margin-right:8px">轮数：</label>
          <input type="number" min="1" max="50" v-model.number="turns" class="turns-input" />
        </div>
        <div class="control-group">
          <button @click="startConversation" :disabled="loading">开始双Agent对话</button>
          <button @click="stopConversation" style="margin-left:8px; background:#f55;">停止对话</button>
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

// 用户输入的问题
const question = ref('')
const question2 = ref('')

// 流式追加的答案内容
const answer = ref('')
// 是否正在加载
const loading = ref(false)
// 选中的模型，支持手动输入
const selectedModel = ref('')
const selectedModel2 = ref('')
const modelList = ref([]) // 模型列表
const currentModel = 1

// SSE 事件源对象
let eventSource = null
// 用于管理所有流式连接，便于批量关闭
const eventSources = []
// 停止标志，用于中断正在运行的对话
const stopRequested = ref(false)

// 对话消息列表：{ speaker: 'Agent1'|'Agent2', text: string }
const messages = ref([])
// 对话轮数（每轮包含双方各一次回复）
const turns = ref(3)

// 模型3 相关
const question3 = ref('')
const selectedModel3 = ref('')
const model3Enabled = ref(false)

// 自动滚动到最新消息
watch(messages, async () => {
  await nextTick()
  const el = document.querySelector('#md')
  if (el) el.scrollTop = el.scrollHeight
})

// 简单的 markdown 渲染助手（用于 messages 列表）
function renderMarkdown(md) {
  try {
    return marked.parse(md || '')
  } catch (e) {
    return md || ''
  }
}

// 单次请求获取模型回复（使用 POST /api/chat 返回 JSON { text }）。
// 由于后端接口不确定，这里以同步 fetch 为主；若需要流式可改用 SSE。
// 使用 SSE 流式接收回复，并实时追加到 messages[idx].text
async function fetchAnswerOnce(prompt, model, idx) {
  return new Promise(async (resolve) => {
    let full = ''
    try {
      const res = await fetch('/api/chat_start', {
        method: 'post',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, model })
      })
      if (!res.ok) {
        const txt = await res.text()
        messages.value[idx].text = `错误：${txt || '启动流失败'}`
        resolve(messages.value[idx].text)
        return
      }
      const streamUrl = await res.text()
      const es = new EventSource(streamUrl)
      // 注册用于批量关闭
      eventSources.push(es)
      es.onmessage = (event) => {
        if (stopRequested.value) {
          // 用户请求停止，关闭连接并返回已接收部分
          try { es.close() } catch (e) { }
          resolve(full)
          return
        }
        if (event.data === '[DONE]') {
          es.close()
          // 从列表中移除
          const si = eventSources.indexOf(es); if (si >= 0) eventSources.splice(si, 1)
          messages.value[idx].text = full
          resolve(full)
          return
        }
        let chunk = ''
        try {
          const data = JSON.parse(event.data)
          chunk = data.text || data.delta || event.data
        } catch (e) {
          chunk = event.data
        }
        full += chunk
        // 实时追加到消息内容中
        messages.value[idx].text = (messages.value[idx].text || '') + chunk
      }
      es.onerror = (e) => {
        console.error('SSE error', e)
        es.close()
        const si = eventSources.indexOf(es); if (si >= 0) eventSources.splice(si, 1)
        messages.value[idx].text = messages.value[idx].text || '流式接收出错'
        resolve(messages.value[idx].text)
      }
    } catch (e) {
      console.error('fetchAnswerOnce exception', e)
      messages.value[idx].text = `错误：${e.message || e}`
      resolve(messages.value[idx].text)
    }
  })
}

// 启动双Agent对话：用 question 作为 Agent1 的初始内容，question2 作为 Agent2 的初始内容
// 交替调用模型，保存每次回复到 messages 列表并渲染
async function startConversation() {
  messages.value = []
  loading.value = true
  stopRequested.value = false
  if (!question.value.trim() || !question2.value.trim()) {
    alert('请为双方都填写初始预设内容（两个输入框）')
    loading.value = false
    return
  }

  // 初始消息
  let lastText = ''
  messages.value.push({ speaker: 'Agent1', text: question.value + '，我的模型是：' + selectedModel.value })
  messages.value.push({ speaker: 'Agent2', text: question2.value + '，我的模型是：' + selectedModel2.value })
  if (model3Enabled.value) {
    messages.value.push({ speaker: 'Agent3', text: question3.value + '，我的模型是：' + selectedModel3.value })
    lastText = question3.value
  } else {
    lastText = question2.value
  }

  // 当前上下文 prompt：取最后一条消息的 text 作为 next prompt
  let lastFromAgent = 'Agent2'
  lastText = question2.value
  for (let i = 0; i < turns.value; i++) {
    if (stopRequested.value) break
    // Agent1 回答（流式）
    const prompt1 = question.value + `，基于\n${lastText}\n，结合情景，完成自己输出自己要做的内容`
    const idx1 = messages.value.push({ speaker: 'Agent1', text: '' }) - 1
    const resp1 = await fetchAnswerOnce(prompt1, selectedModel.value, idx1)
    lastText = resp1
    if (stopRequested.value) break

    // Agent2 回答（流式）

    // 结束时清理所有 eventSources
    try { eventSources.forEach(es => es.close()) } catch (e) { }
    eventSources.length = 0
    loading.value = false
    const prompt2 = question2.value + `，基于\n${lastText}\n，结合情景，完成自己输出自己要做的内容`

    function stopConversation() {
      stopRequested.value = true
      // 立即关闭所有 EventSource
      try { eventSources.forEach(es => es.close()) } catch (e) { }
      eventSources.length = 0
      loading.value = false
    }
    const idx2 = messages.value.push({ speaker: 'Agent2', text: '' }) - 1
    const resp2 = await fetchAnswerOnce(prompt2, selectedModel2.value, idx2)
    lastText = resp2
    // Agent3 回答（可选，流式）
    if (model3Enabled.value) {
      // 取最近两条消息（通常是 Agent1 和 Agent2 的回复），先让 Agent3 做简短总结再回答
      const recent = messages.value.slice(-2).map(m => `${m.speaker}: ${m.text}`).join('\n')
      const prompt3 = `${question3.value}\n\n请先用不少于500字浓缩总结下面两条内容的要点（要点式列出）， 包裹总结内容：\n${recent}\n\n 结合情景，完成自己输出自己要做的内容。`;
      const idx3 = messages.value.push({ speaker: 'Agent3', text: '' }) - 1
      const resp3 = await fetchAnswerOnce(prompt3, selectedModel3.value, idx3)
      lastText = resp3
    }
  }

  loading.value = false
}

// 配置 marked 支持代码高亮
marked.setOptions({
  highlight: function (code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      // 指定语言高亮
      return hljs.highlight(code, { language: lang }).value
    }
    // 自动检测语言高亮
    return hljs.highlightAuto(code).value
  }
})

// 响应式渲染 markdown 内容
const renderedAnswer = computed(() => marked.parse(answer.value))

// 每次 markdown 内容变化后，自动高亮代码块
watch(renderedAnswer, async () => {
  await nextTick()
  document.querySelectorAll('#md pre code').forEach(block => hljs.highlightElement(block))
})

// 提交问题，流式获取答案
function askQuestion(questionText, model, agentIndex = 1) {
  answer.value = ''
  loading.value = true
  if (!questionText.trim()) {
    alert('不允许空问题，请输入详细的问题哦！')
    loading.value = false
    return
  }
  // 关闭旧的 SSE 连接
  if (eventSource) {
    eventSource.close()
  }
  // 使用 fetch 先 POST，获取流式 EventSource 通道
  fetch('/api/chat_start', {
    method: 'post',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      prompt: questionText,
      model: model
    })
  }).then(res => {
    if (!res.ok) throw new Error('接口请求失败')
    // 假设后端返回一个流式通道地址
    return res.text()
  }).then((streamUrl) => {
    eventSource = new EventSource(streamUrl)
    eventSource.onmessage = (event) => {
      // 检查流式消息是否为结束标志
      if (event.data === '[DONE]') {
        loading.value = false
        eventSource.close()
        return
      }
      try {
        const data = JSON.parse(event.data)
        if (data.text) {
          answer.value += data.text
        }
      } catch (e) {
        answer.value += event.data
      }
    }
    eventSource.onerror = () => {
      loading.value = false
      eventSource.close()
    }
    eventSource.onopen = () => {
      // loading already set to true at function start
    }
    eventSource.addEventListener('end', () => {
      loading.value = false
      eventSource.close()
    })
  }).catch(() => {
    loading.value = false
    answer.value = '接口调用失败，请稍后重试。'
  })
}

// 页面初始化时获取模型列表
onMounted(async () => {
  try {
    const res = await fetch('/api/models')
    const data = await res.json()
    modelList.value = data.models || []
    // 默认选中第一个模型
    if (modelList.value.length > 0) {
      selectedModel.value = modelList.value[0]
      selectedModel2.value = modelList.value[0]
      selectedModel3.value = modelList.value[0]
    }
  } catch (e) {
    // 如果接口异常，使用默认模型列表
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
    selectedModel2.value = modelList.value[1] || modelList.value[0]
    selectedModel3.value = modelList.value[2] || modelList.value[0]
  }
})
</script>

<style scoped>
/* 页面整体样式，居中并全屏 */
.qna-page {
  min-height: 100vh;
  /* 页面最小高度为视口高度，实现全屏 */
  width: 100vw;
  /* 页面宽度为视口宽度，实现全屏 */
  box-sizing: border-box;
  /* 让 padding 和 border 包含在 width/height 内 */
  padding: 0;
  margin: 0;
  display: flex;
  /* 使用 flex 布局，方便垂直排列内容 */
  flex-direction: column;
  /* 子元素垂直排列 */
  align-items: center;
  /* 子元素水平居中 */
  background: #f4f6fb;
  /* 浅灰蓝色背景，提升页面质感 */
}

/* 标题样式 */
h2 {
  margin-top: 48px;
  /* 顶部留白 */
  margin-bottom: 24px;
  /* 标题下方留白 */
  font-size: 2em;
  /* 字体放大 */
  font-weight: 600;
  /* 加粗 */
  color: #333;
  /* 深色字体 */
}

/* 答案区域样式 */
.answer {
  width: 80%;
  max-width: 1200px;
  height: 480px;
  margin: 24px auto;
  font-size: 1em;
  white-space: pre-wrap;
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  box-sizing: border-box;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  overflow-y: auto;
}

/* 输入区域样式 */
.input-area {
  width: 80vw;
  /* 输入区宽度与答案区一致 */
  max-width: 77vw;
  /* 最大宽度，防止超大屏幕过宽 */
  display: flex;
  /* 横向排列输入框、下拉框和按钮 */
  gap: 12px;
  /* 输入框、下拉框和按钮之间的间距 */
  align-items: center;
  /* 垂直居中 */
  margin-bottom: 12px;
  /* 底部留白 */
}

/* 将最后一个输入区域固定在底部并居中 */

/* 底部固定容器，包含所有输入区域 */
.bottom-bar {
  position: fixed;
  left: 50%;
  transform: translateX(-50%);
  bottom: 18px;
  width: 80%;
  max-width: 1100px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  justify-content: center;
  background: rgba(255, 255, 255, 0.95);
  padding: 12px 16px;
  border-radius: 10px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
  z-index: 40;
}

.bottom-bar .bar-row {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-bottom: 8px;
}

.bottom-bar .input-area {
  width: 100%;
  max-width: 1000px;
  display: flex;
  gap: 12px;
  align-items: center;
  margin: 0;
}

.control-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.turns-input {
  flex: 1;
  padding: 6px;
  margin-left: 8px;
  margin-right: 16px;
  border-radius: 6px;
  border: 1px solid #ccc;
}

@media (max-width: 800px) {
  .bottom-bar {
    width: 94%;
    padding: 10px;
    flex-direction: column;
    align-items: stretch;
  }

  .bottom-bar .input-area {
    flex-direction: column;
    align-items: stretch;
  }

  .control-row {
    flex-direction: column-reverse;
    gap: 8px;
  }
}

.message-item {
  margin: 12px 0;
  display: flex;
  flex-direction: column;
}

.message-item .meta {
  font-size: 0.9em;
  color: #666;
  margin-bottom: 6px;
}

.message-item .bubble {
  max-width: 70%;
  padding: 12px;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  white-space: pre-wrap;
  font-size: 0.98em;
}

.message-item.agent1 {
  align-items: flex-start;
}

.message-item.agent1 .bubble {
  background: #eef6ff;
  color: #062a4f;
  border-top-left-radius: 4px;
}

.message-item.agent2 {
  align-items: flex-end;
}

.message-item.agent2 .bubble {
  background: #fff6ea;
  color: #4a2b00;
  border-top-right-radius: 4px;
}

.message-item.agent3 {
  align-items: center;
}

.message-item.agent3 .bubble {
  background: #f3f0ff;
  color: #2f1652;
}

/* 输入框样式 */
input {
  flex: 2;
  /* 输入框占较大空间 */
  padding: 12px;
  /* 内边距，提升输入体验 */
  font-size: 1em;
  /* 字体适中 */
  border-radius: 6px;
  /* 圆角 */
  border: 1px solid #ccc;
  /* 浅灰色边框 */
  background: #f8f8fa;
  /* 浅灰背景，区分于内容区 */
}

/* 模型选择输入框样式 */
.model-select {
  flex: 1;
  /* 下拉框占较小空间 */
  padding: 12px;
  font-size: 1em;
  border-radius: 6px;
  border: 1px solid #ccc;
  background: #f8f8fa;
}

/* 移除 datalist 下拉箭头样式 */
.model-select::-webkit-calendar-picker-indicator {
  opacity: 0.6;
  /* 使下拉箭头略微透明 */
  cursor: pointer;
  /* 鼠标悬停变为手型 */
}

/* 按钮样式 */
button {
  padding: 12px 24px;
  /* 按钮内边距，提升点击区域 */
  font-size: 1em;
  /* 字体适中 */
  border-radius: 6px;
  /* 圆角 */
  border: none;
  /* 去除默认边框 */
  background: #4f8cff;
  /* 蓝色背景，突出按钮 */
  color: #fff;
  /* 白色字体 */
  cursor: pointer;
  /* 鼠标悬停变为手型 */
  transition: background 0.2s;
  /* 背景色渐变过渡，提升交互体验 */
}

/* 按钮禁用样式 */
button:disabled {
  background: #b0c4e6;
  /* 禁用时变为浅蓝色 */
  cursor: not-allowed;
  /* 鼠标悬停变为禁止符号 */
}
</style>