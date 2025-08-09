<template>
  <div class="qna-page">
    <h2>外包开发助手</h2>
    <div>
      <p>项目管理、产品设计、需求设计、技术方案一应俱全！</p>
    </div>
    <div>
      <h3>您的问题：{{ question }}</h3>
    </div>
    <div class="answer" id="md">
      <span v-if="loading">正在生成答案...</span>
      <div v-html="renderedAnswer"></div>
    </div>
    <div class="input-area">
      <input v-model="question" placeholder="请输入你的问题..." />
      <button @click="askQuestion" :disabled="loading">提交</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

const question = ref('')
const answer = ref('')
const loading = ref(false)
let eventSource = null

marked.setOptions({
  highlight: function (code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  }
})

const renderedAnswer = computed(() => marked.parse(answer.value))

watch(renderedAnswer, async () => {
  await nextTick()
  document.querySelectorAll('#md pre code').forEach(block => hljs.highlightElement(block))
})

function askQuestion() {
  answer.value = ''
  loading.value = true
  if (eventSource) {
    eventSource.close()
  }
  eventSource = new EventSource(`/api/chat?prompt=${encodeURIComponent(question.value)}`)
  eventSource.onmessage = (event) => {
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
    loading.value = true
  }
  eventSource.addEventListener('end', () => {
    loading.value = false
    eventSource.close()
  })
}
</script>

<style scoped>
.qna-page {
  min-height: 100vh;
  width: 100vw;
  box-sizing: border-box;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #f4f6fb;
}

h2 {
  margin-top: 48px;
  margin-bottom: 24px;
  font-size: 2em;
  font-weight: 600;
  color: #333;
}

.answer {
  width: 80vw;
  flex: 1;
  margin-bottom: 24px;
  font-size: 1.1em;
  min-height: 200px;
  white-space: pre-wrap;
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  box-sizing: border-box;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  overflow-y: auto;
}

.input-area {
  width: 80vw;
  max-width: 900px;
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 48px;
}

input {
  flex: 1;
  padding: 12px;
  font-size: 1em;
  border-radius: 6px;
  border: 1px solid #ccc;
  background: #f8f8fa;
}

button {
  padding: 12px 24px;
  font-size: 1em;
  border-radius: 6px;
  border: none;
  background: #4f8cff;
  color: #fff;
  cursor: pointer;
  transition: background 0.2s;
}

button:disabled {
  background: #b0c4e6;
  cursor: not-allowed;
}
</style>