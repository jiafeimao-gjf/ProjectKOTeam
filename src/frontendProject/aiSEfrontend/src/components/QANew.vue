<template>
  <div class="qa-new-page">
    <header class="qa-header">
      <h1>Assistant — 新界面（交互与 QnA 相同）</h1>
      <p class="subtitle">左侧为对话历史，右侧为控制面板（模型选择 / 系统提示 / 输入）</p>
    </header>

    <main class="qa-main">
      <section class="conversation" ref="conversationContainer">
        <div v-if="QAHistory.length === 0 && !loading" class="empty">
          <div class="empty-illustration">🗨️</div>
          <h3>开始对话</h3>
          <p>你的交互记录会在此处显示</p>
        </div>

        <div v-for="(qa, idx) in QAHistory" :key="idx" class="card">
          <div class="card-header">
            <div class="tag">Q {{ idx + 1 }}</div>
            <div class="meta">{{ qa.model }} · {{ qa.timestamp || '' }}</div>
          </div>

          <div class="card-body">
            <div class="question-block">
              <div class="label">你</div>
              <pre class="content">{{ qa.question }}</pre>
              <button class="copy-btn" @click="copyMessage(qa.question)">复制</button>
            </div>

            <div class="answer-block">
              <div class="a-label">AI</div>
              <div class="answer-content">
                <div v-if="idx === currentAnswerIndex && isStreaming" class="streaming-text">{{ qa.answer }}<span class="typing-cursor">|</span></div>
                <div v-else v-html="getRenderedAnswer(idx)"></div>
              </div>
              <button class="copy-btn" @click="copyMessage(getRenderedAnswerPlain(idx))">复制</button>
            </div>
          </div>
        </div>

      </section>

      <aside class="control">
        <div class="control-card">
          <label class="label">模型</label>
          <select v-model="selectedModel" class="model-select">
            <option v-for="m in modelList" :key="m" :value="m">{{ m }}</option>
          </select>

          <label class="label">系统提示（可选）</label>
          <textarea v-model="systemPrompt" placeholder="输入系统提示..." class="system-area"></textarea>

          <label class="label">提问</label>
          <textarea v-model="question" placeholder="输入你的问题" class="question-area" @keydown.enter.exact.prevent="askQuestion" @keydown.enter.shift.exact="handleShiftEnter"></textarea>

          <div class="controls">
            <button class="btn primary" @click="askQuestion" :disabled="loading || !question.trim()">{{ loading ? '思考中...' : '发送' }}</button>
            <button class="btn" @click="clearHistory">清空记录</button>
          </div>

          <div class="help">说明：此界面只是 UI 改造，功能与旧版一致，支持流式返回、复制、代码高亮等。</div>
        </div>
      </aside>
    </main>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import DOMPurify from 'dompurify'

// state
const question = ref('')
const systemPrompt = ref('')
const loading = ref(false)
const selectedModel = ref('')
const modelList = ref([])
const QAHistory = ref([])
const conversationContainer = ref(null)
const isStreaming = ref(false)
const currentAnswerIndex = ref(-1)

let eventSource = null

// marked config
marked.setOptions({
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) return hljs.highlight(code, { language: lang }).value
    return hljs.highlightAuto(code).value
  },
  gfm: true,
  breaks: true
})

function handleShiftEnter() {
  nextTick(() => {})
}

function copyMessage(text) {
  try {
    if (!text) return
    const plain = ('' + text).replace(/<[^>]*>/g, '')
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(plain)
    } else {
      const ta = document.createElement('textarea')
      ta.value = plain
      document.body.appendChild(ta)
      ta.select()
      document.execCommand('copy')
      ta.remove()
    }
    // quick toast
    const t = document.createElement('div')
    t.className = 'copy-toast'
    t.innerText = '\u2713 已复制'
    document.body.appendChild(t)
    setTimeout(() => t.remove(), 1300)
  } catch (e) {
    console.error('copy fail', e)
  }
}

function getRenderedAnswer(index) {
  const qa = QAHistory.value[index]
  if (!qa || !qa.answer) return ''
  if (index === currentAnswerIndex.value && isStreaming.value) return qa.answer
  const html = marked.parse(qa.answer)
  return DOMPurify.sanitize(html)
}

function getRenderedAnswerPlain(index) {
  const html = getRenderedAnswer(index) || ''
  // return plain text
  const div = document.createElement('div')
  div.innerHTML = html
  return div.innerText || div.textContent || ''
}

function scrollToBottom() {
  nextTick(() => {
    if (conversationContainer.value) {
      conversationContainer.value.scrollTop = conversationContainer.value.scrollHeight
    }
  })
}

function highlightCodeBlocks() {
  nextTick(() => {
    if (!conversationContainer.value) return
    conversationContainer.value.querySelectorAll('pre code').forEach(b => {
      if (b.textContent.trim()) hljs.highlightElement(b)
    })
  })
}

watch(() => QAHistory.value.map(x => x.answer), async () => {
  await nextTick()
  scrollToBottom()
  if (!isStreaming.value) highlightCodeBlocks()
})

async function askQuestion() {
  if (!question.value.trim()) return
  loading.value = true
  isStreaming.value = true
  const qa = {
    question: (systemPrompt.value || '') + question.value,
    model: selectedModel.value,
    answer: '',
    timestamp: new Date().toLocaleString()
  }
  QAHistory.value.push(qa)
  currentAnswerIndex.value = QAHistory.value.length - 1
  const proto = question.value
  question.value = ''

  if (eventSource) try { eventSource.close() } catch (e) {}

  try {
    const res = await fetch('/api/chat_start', {
      method: 'post',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: qa.question, model: selectedModel.value })
    })
    if (!res.ok) throw new Error('接口请求失败')
    const streamUrl = await res.text()
    eventSource = new EventSource(streamUrl)
    eventSource.onmessage = (evt) => {
      if (evt.data === '[DONE]') {
        loading.value = false
        isStreaming.value = false
        try { eventSource.close() } catch (e) {}
        highlightCodeBlocks()
        return
      }
      try {
        const data = JSON.parse(evt.data)
        if (data.text) QAHistory.value[currentAnswerIndex.value].answer += data.text
      } catch (e) {
        QAHistory.value[currentAnswerIndex.value].answer += evt.data
      }
    }
    eventSource.onerror = () => {
      loading.value = false
      isStreaming.value = false
      try { eventSource.close() } catch (e) {}
      QAHistory.value[currentAnswerIndex.value].answer = '连接中断，请重试。'
    }
    eventSource.addEventListener('end', () => {
      loading.value = false
      isStreaming.value = false
      try { eventSource.close() } catch (e) {}
    })
  } catch (err) {
    loading.value = false
    isStreaming.value = false
    QAHistory.value[currentAnswerIndex.value].answer = '请求失败，请检查网络连接。'
    console.error(err)
  }
}

function clearHistory() {
  QAHistory.value.length = 0
}

onMounted(async () => {
  try {
    const res = await fetch('/api/models')
    const data = await res.json()
    modelList.value = data.models || [
      'gpt-oss:20b', 'deepseek-r1:8b', 'deepseek-r1:32b', 'gemma3n:e4b', 'llama3.1:8b', 'llama2:latest'
    ]
    if (modelList.value.length > 0) selectedModel.value = modelList.value[0]
  } catch (e) {
    modelList.value = ['gpt-oss:20b']
    selectedModel.value = modelList.value[0]
  }
  // add resize handler to adjust scroll (if needed)
  window.addEventListener('resize', () => scrollToBottom())
})

onUnmounted(() => {
  if (eventSource) try { eventSource.close() } catch (e) {}
  window.removeEventListener('resize', () => scrollToBottom())
})
</script>

<style scoped>
:root { --card-bg: #fdfdfd }
.qa-new-page { padding: 24px; width: 100%; box-sizing: border-box }
.qa-header { text-align: center; margin-bottom: 16px }
.qa-main { display: grid; grid-template-columns: 1fr 360px; gap: 20px }
.conversation { background: var(--card-bg); border-radius: 8px; padding: 16px; max-height: 72vh; overflow-y: auto }
.control { position: sticky; top: 24px }
.control-card { background: #fff; border-radius: 8px; padding: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.06) }
.card { margin-bottom: 16px; border-radius: 8px; padding: 12px; background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,0.04) }
.card-header{ display:flex; justify-content:space-between; align-items:center; gap:8px; margin-bottom:8px }
.tag{ font-weight:bold; background: linear-gradient(90deg,#6366f1,#8b5cf6); color:#fff; padding:4px 8px; border-radius:6px }
.card-body{ display:flex; flex-direction:column; gap:10px }
.label,.a-label{ font-size:12px; color:#64748b; font-weight:600 }
.question-block pre,.answer-block .content{ margin:0; white-space:pre-wrap; background:#f8fafc; padding:8px; border-radius:6px }
.copy-btn{ margin-top:8px; padding:6px 10px; border-radius:6px; background:#f1f5f9; border:1px solid #e2e8f0; cursor:pointer }
.copy-toast{ position:fixed; right:20px; bottom:20px; background:#333; color:#fff; padding:8px 10px; border-radius:6px }
.system-area,.question-area{ width:100%; min-height:70px; border-radius:6px; border:1px solid #e2e8f0; padding:8px; resize:vertical }
.model-select{ width:100%; padding:8px; border-radius:6px; border:1px solid #e2e8f0; }
.btn{ padding:8px 12px; border-radius:6px; border:none; cursor:pointer; background:#f1f5f9 }
.btn.primary{ background: linear-gradient(90deg,#6366f1,#8b5cf6); color:#fff }
.help{ margin-top:12px; color:#94a3b8; font-size:12px }
.streaming-text{ white-space:pre-wrap }
.typing-cursor{ margin-left:4px; color:#6366f1 }

@media (max-width: 900px) { .qa-main { grid-template-columns: 1fr } .control { position: relative; top: auto } }
</style>