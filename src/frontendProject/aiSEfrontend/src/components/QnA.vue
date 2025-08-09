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
      <!-- 加载中提示 -->
      <span v-if="loading">正在生成答案...</span>
      <!-- 渲染 markdown 格式的答案 -->
      <div v-html="renderedAnswer"></div>
    </div>
    <div class="input-area">
      <!-- 问题输入框 -->
      <input v-model="question" placeholder="请输入你的问题..." />
      <!-- 提交按钮，加载时禁用 -->
      <button @click="askQuestion" :disabled="loading">提交</button>
    </div>
  </div>
</template>

<script setup>
// Vue 响应式 API
import { ref, computed, watch, nextTick } from 'vue'
// markdown 解析库
import { marked } from 'marked'
// 代码高亮库
import hljs from 'highlight.js'
// 代码高亮样式
import 'highlight.js/styles/github.css'

// 用户输入的问题
const question = ref('')
// 流式追加的答案内容
const answer = ref('')
// 是否正在加载
const loading = ref(false)
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

// 响应式渲染 markdown 内容
const renderedAnswer = computed(() => marked.parse(answer.value))

// 每次 markdown 内容变化后，自动高亮代码块
watch(renderedAnswer, async () => {
  await nextTick()
  document.querySelectorAll('#md pre code').forEach(block => hljs.highlightElement(block))
})

// 提交问题，流式获取答案
function askQuestion() {
  answer.value = ''
  loading.value = true
  // 关闭旧的 SSE 连接
  if (eventSource) {
    eventSource.close()
  }
  // 建立新的 SSE 连接，请求后端接口
  eventSource = new EventSource(`/api/chat?prompt=${encodeURIComponent(question.value)}`)
  eventSource.onmessage = (event) => {
    try {
      // 解析后端返回的 JSON 数据
      const data = JSON.parse(event.data)
      if (data.text) {
        // 流式追加答案内容
        answer.value += data.text
      }
    } catch (e) {
      // 非 JSON 格式直接追加
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
  max-width: 900px;          /* 最大宽度，防止超大屏幕过宽 */
  display: flex;             /* 横向排列输入框和按钮 */
  gap: 12px;                 /* 输入框和按钮之间的间距 */
  align-items: center;       /* 垂直居中 */
  margin-bottom: 48px;       /* 底部留白 */
}

/* 输入框样式 */
input {
  flex: 1;                   /* 输入框自动填满剩余空间 */
  padding: 12px;             /* 内边距，提升输入体验 */
  font-size: 1em;            /* 字体适中 */
  border-radius: 6px;        /* 圆角 */
  border: 1px solid #ccc;    /* 浅灰色边框 */
  background: #f8f8fa;       /* 浅灰背景，区分于内容区 */
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