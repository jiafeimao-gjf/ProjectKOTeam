<template>
  <div class="qna-page">
    <h2>本地agent助手</h2>
    <div class="answer" id="md">
      <div v-for="(qa, index) in QAHistory" :key="index" class="qa-item">
        <p style="text-align: left">你：</p>
        <div class="qa-question">
          <div class="meta"><strong>{{ qa.question }}</strong></div>
        </div>
        <p style="text-align: right">agent回答：</p>
        <div class="bubble">
          <div class="meta"><strong>模型: {{ qa.model }} </strong></div>
          <!-- 加载中提示 -->
          <span v-if="loading">正在生成答案...</span>
          <div v-html="getRenderedAnswer(index)"></div>
        </div>
      </div>

    </div>
    <div class="input-area">
      <textarea v-model="systemPrompt" placeholder="前置约束提示词" class="question-input"
        ref="questionTextarea"></textarea>
    </div>

    <div class="input-area">
      <!-- 问题输入框 -->
      <textarea v-model="question" placeholder="请输入你的问题..." class="question-input" ref="questionTextarea"></textarea>
      <!-- 模型选择下拉框，始终可见所有模型 -->
      <select v-model="selectedModel" class="model-select">
        <option v-for="model in modelList" :key="model" :value="model">{{ model }}</option>
      </select>
      <!-- 提交按钮，加载时禁用 -->
      <button @click="askQuestion" :disabled="loading">提交</button>
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
const systemPrompt = ref('')
// 是否正在加载
const loading = ref(false)
// 选中的模型，支持手动输入
const selectedModel = ref('')
const modelList = ref([]) // 模型列表

const QAHistory = ref([])
const questionTextarea = ref(null) // 文本域引用

// SSE 事件源对象
let eventSource = null

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

function getLastAnswer() {
  if (QAHistory.value && QAHistory.value.length === 0) {
    return ''
  }
  const qaTemp = QAHistory.value[QAHistory.value.length - 1]
  return qaTemp.answer
}

function getRenderedAnswer(index) {
  const qaTemp = QAHistory.value[index]
  return marked.parse(qaTemp.answer)
}

// 每次 markdown 内容变化后，自动高亮代码块
watch(QAHistory, async () => {
  await nextTick()
  document.querySelectorAll('#md pre code').forEach(block => hljs.highlightElement(block))
})

// 提交问题，流式获取答案
function askQuestion() {
  loading.value = true

  if (!question.value.trim()) {
    alert('不允许空问题，请输入详细的问题哦！')
    loading.value = false
    return
  }
  let qa = {
    question: systemPrompt.value + "\n" + question.value,
    model: selectedModel.value,
    answer: ''
  }

  QAHistory.value.push(qa)

  // 清空输入框并重置高度
  question.value = ''
  adjustTextareaHeight()

  // 关闭旧的 SSE 连接
  if (eventSource) {
    eventSource.close()
  }
  // 使用 fetch 先 POST，获取流式 EventSource 通道
  fetch('/api/chat_start', {
    method: 'post',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      prompt: qa.question,
      model: selectedModel.value
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
          QAHistory.value[QAHistory.value.length - 1].answer += data.text
        }
      } catch (e) {
        QAHistory.value[QAHistory.value.length - 1].answer += event.data
      }
    }
    eventSource.onerror = () => {
      loading.value = false
      eventSource.close()
    }
  }).catch(() => {
    loading.value = false
    QAHistory.value[QAHistory.value.length - 1].answer = '接口调用失败，请稍后重试。'
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
  width: 80vw;
  /* 答案区域宽度为视口的 80% */
  flex: 1;
  /* 占据剩余空间，保证内容区自适应高度 */
  margin-bottom: 24px;
  /* 底部留白 */
  font-size: 1.1em;
  /* 字体稍大 */
  min-height: 200px;
  /* 最小高度，防止内容太少时塌陷 */
  white-space: pre-wrap;
  /* 保留空格和换行，适合 markdown 内容 */
  background: #fff;
  /* 白色背景，突出内容区 */
  padding: 24px;
  /* 内边距，内容不贴边 */
  border-radius: 8px;
  /* 圆角，提升美观 */
  box-sizing: border-box;
  /* 让 padding 包含在 width 内 */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  /* 轻微阴影，提升层次感 */
  overflow-y: auto;
  /* 内容超出时可滚动 */
}

.answer .meta {
  font-size: 0.9em;
  color: #666;
  margin-bottom: 6px;
}

.answer .qa-question {
  align-items: flex-start;
  width: auto;
  font-size: 1.1em;
  /* 字体稍大 */
  font-weight: 600;
  /* 加粗 */
  color: #333;
  /* 深色字体 */
  margin-bottom: 12px;
  /* 底部留白 */
  padding: 12px;
  /* 内边距，提升可读性 */
  border-radius: 6px;
  /* 圆角，提升美观 */
  background: #f8f8fa;
  /* 浅灰背景，区分于内容区 */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  /* 轻微阴影，提升层次感 */
  margin-top: 10px;
}

.answer .bubble {
  align-items: flex-start;
  width: auto;
  padding: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  white-space: pre-wrap;
  font-size: 0.98em;
  background: #eef6ff;
  color: #062a4f;
  border-top-left-radius: 4px;
  text-align: left;
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
  margin-bottom: 48px;
  /* 底部留白 */
}

/* 输入框样式 */
.question-input {
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
  resize: vertical;
  /* 只允许垂直方向调整大小 */
  min-height: 40px;
  /* 最小高度 */
  max-height: 200px;
  /* 最大高度 */
  font-family: inherit;
  /* 使用系统默认字体 */
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