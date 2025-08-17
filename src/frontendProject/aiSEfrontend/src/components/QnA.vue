<template>
  <div class="qna-page">
    <h2>本地agent助手</h2>
    <div class="history">
        <!-- 历史问答列表 -->
        <div v-for="(item, idx) in history" :key="item.id" class="qa-item">
          <h3>问题 {{ idx + 1 }}：{{ item.question }}</h3>
          <div class="meta">模型：{{ item.model }} · 提问时间：{{ item.timestamp }}</div>
          <div class="answer" :id="'answer-' + item.id">
            <span v-if="item.loading">正在生成答案...</span>
            <div v-html="renderMarkdown(item.answer)" :ref="el => { if (el) answerElements[item.id] = el }"></div>
          </div>
        </div>
      </div>
    <div class="input-area">
      <!-- 问题输入框 -->
      <input v-model="question" placeholder="请输入你的问题..." />
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
// 每一轮问答历史（不会因为下一次问答而被清空）
const history = ref([]) // [{id, question, answer, model, loading, timestamp}]
// 全局是否有正在流式生成的轮次（用于禁用提交按钮）
const anyLoading = computed(() => history.value.some(h => h.loading))
// 选中的模型，支持手动输入
const selectedModel = ref('')
const modelList = ref([]) // 模型列表
// 用于存储答案元素的引用
const answerElements = ref({})

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

// 渲染指定文本为 markdown
function renderMarkdown(text) {
  return marked.parse(text || '')
}

// 当历史中任意答案变化时，下一次 DOM 更新后高亮代码块
watch(() => history.value.map(h => h.answer), async () => {
  await nextTick()
  // 为每个答案区域单独处理代码高亮
  Object.values(answerElements.value).forEach(element => {
    if (element) {
      element.querySelectorAll('pre code').forEach(block => {
        hljs.highlightElement(block)
      })
    }
  })
}, { deep: true })

// 提交问题，流式获取答案
function askQuestion() {
  if (!question.value.trim()) {
    alert('不允许空问题，请输入详细的问题哦！')
    return
  }

  // 创建新的轮次并加入历史，保留以前所有内容
  const entry = {
    id: Date.now(),
    question: question.value,
    answer: '',
    model: selectedModel.value,
    loading: true,
    timestamp: new Date().toLocaleString()
  }
  history.value.push(entry)

  // 关闭旧的 SSE 连接（如果存在）
  if (eventSource) {
    try { eventSource.close() } catch (e) {}
  }

  // POST 获取流式 EventSource 通道地址，然后对该轮次进行流式追加
  fetch('/api/chat_start', {
    method: 'post',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      prompt: entry.question,
      model: entry.model
    })
  }).then(res => {
    if (!res.ok) throw new Error('接口请求失败')
    return res.text()
  }).then((streamUrl) => {
    eventSource = new EventSource(streamUrl)
    eventSource.onmessage = (event) => {
      if (event.data === '[DONE]') {
        entry.loading = false
        try { eventSource.close() } catch (e) {}
        return
      }
      try {
        const data = JSON.parse(event.data)
        if (data.text) entry.answer += data.text
      } catch (e) {
        entry.answer += event.data
      }
    }
    eventSource.onerror = () => {
      entry.loading = false
      try { eventSource.close() } catch (e) {}
    }
    eventSource.onopen = () => {
      entry.loading = true
    }
    eventSource.addEventListener('end', () => {
      entry.loading = false
      try { eventSource.close() } catch (e) {}
    })
  }).catch(() => {
    entry.loading = false
    entry.answer = '接口调用失败，请稍后重试。'
  })

  // 清空输入框（保留历史）
  question.value = ''
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
  min-height: 100vh;         /* 页面最小高度为视口高度，实现全屏 */
  width: 100vw;              /* 页面宽度为视口宽度，实现全屏 */
  box-sizing: border-box;    /* 让 padding 和 border 包含在 width/height 内 */
  padding: 0;
  margin: 0;
  display: flex;             /* 使用 flex 布局，方便垂直排列内容 */
  flex-direction: column;    /* 子元素垂直排列 */
  align-items: center;       /* 子元素水平居中 */
  background: #f4f6fb;       /* 浅灰蓝色背景，提升页面质感 */
}

/* 标题样式 */
h2 {
  margin-top: 48px;          /* 顶部留白 */
  margin-bottom: 24px;       /* 标题下方留白 */
  font-size: 2em;            /* 字体放大 */
  font-weight: 600;          /* 加粗 */
  color: #333;               /* 深色字体 */
}

/* 答案区域样式 */
.answer {
  width: 80vw;               /* 答案区域宽度为视口的 80% */
  flex: 1;                   /* 占据剩余空间，保证内容区自适应高度 */
  margin-bottom: 24px;       /* 底部留白 */
  font-size: 1.1em;          /* 字体稍大 */
  min-height: 200px;         /* 最小高度，防止内容太少时塌陷 */
  white-space: pre-wrap;     /* 保留空格和换行，适合 markdown 内容 */
  background: #fff;          /* 白色背景，突出内容区 */
  padding: 24px;             /* 内边距，内容不贴边 */
  border-radius: 8px;        /* 圆角，提升美观 */
  box-sizing: border-box;    /* 让 padding 包含在 width 内 */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04); /* 轻微阴影，提升层次感 */
  overflow-y: auto;          /* 内容超出时可滚动 */
}

/* 输入区域样式 */
.input-area {
  width: 80vw;               /* 输入区宽度与答案区一致 */
  max-width: 77vw;          /* 最大宽度，防止超大屏幕过宽 */
  display: flex;             /* 横向排列输入框、下拉框和按钮 */
  gap: 12px;                 /* 输入框、下拉框和按钮之间的间距 */
  align-items: center;       /* 垂直居中 */
  margin-bottom: 48px;       /* 底部留白 */
}

/* 输入框样式 */
input {
  flex: 2;                   /* 输入框占较大空间 */
  padding: 12px;             /* 内边距，提升输入体验 */
  font-size: 1em;            /* 字体适中 */
  border-radius: 6px;        /* 圆角 */
  border: 1px solid #ccc;    /* 浅灰色边框 */
  background: #f8f8fa;       /* 浅灰背景，区分于内容区 */
}

/* 模型选择输入框样式 */
.model-select {
  flex: 1;                   /* 下拉框占较小空间 */
  padding: 12px;
  font-size: 1em;
  border-radius: 6px;
  border: 1px solid #ccc;
  background: #f8f8fa;
}

/* 移除 datalist 下拉箭头样式 */
.model-select::-webkit-calendar-picker-indicator {
  opacity: 0.6;             /* 使下拉箭头略微透明 */
  cursor: pointer;          /* 鼠标悬停变为手型 */
}

/* 按钮样式 */
button {
  padding: 12px 24px;        /* 按钮内边距，提升点击区域 */
  font-size: 1em;            /* 字体适中 */
  border-radius: 6px;        /* 圆角 */
  border: none;              /* 去除默认边框 */
  background: #4f8cff;       /* 蓝色背景，突出按钮 */
  color: #fff;               /* 白色字体 */
  cursor: pointer;           /* 鼠标悬停变为手型 */
  transition: background 0.2s; /* 背景色渐变过渡，提升交互体验 */
}

/* 按钮禁用样式 */
button:disabled {
  background: #b0c4e6;       /* 禁用时变为浅蓝色 */
  cursor: not-allowed;       /* 鼠标悬停变为禁止符号 */
}
</style>