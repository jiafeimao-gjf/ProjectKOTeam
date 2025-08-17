<template>
  <div class="project-engine">
    <h2>软件项目孵化链式思考内容生成工具</h2>
    <!-- 每个输入框单独一行 -->
    <div class="input-area">
      <div class="input-area">
        <div class="input-row">
          <input v-model="projectDesc" placeholder="请输入初始需求描述..." />
        </div>
      </div>
      <!-- 选择区和按钮一行 -->
      <div class="select-row">
        <p>模型选择:</p>
        <select v-model="selectedModel" class="model-select">
          <option v-for="model in modelList" :key="model" :value="model">{{ model }}</option>
        </select>
        <p>反复问答次数:</p>
        <input type="number" min="1" max="1000" v-model.number="stepCount" placeholder="链式步数(默认5)" class="step-input" />
        <button @click="startChain" :disabled="loading || !projectDesc">开始链式分析</button>
      </div>
    </div>
    <!-- 展示 prompts 列表 -->
    <div class="prompts-list">
      <div v-for="(prompt, idx) in prompts" :key="idx" class="prompt-item">
        <strong>第 {{ idx + 1 }} 个提示词：</strong> {{ prompt }}
      </div>
    </div>
    <div class="chain-result">
      <div v-for="(node, idx) in chainNodes" :key="idx" class="chain-node">
        <h3>第{{ idx + 1 }}步</h3>
        <div v-html="node.answer"></div>
        <div v-if="node.summary" v-html="node.summary" style="margin-top:12px;color:#4f8cff;"></div>
      </div>
      <span v-if="loading">正在链式分析...</span>
    </div>
  </div>
</template>

<script setup>

import { ref, onMounted, nextTick } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import { fetchStreamAnswer } from '../utils/llm.js'

const projectDesc = ref('')
const firstAnswer = ref('')

const selectedModel = ref('')
const modelList = ref([])
const chainNodes = ref([])
const loading = ref(false)
const stepCount = ref(5) // 步数，默认5步
const prompts = ref([])

// 初始化模型列表
onMounted(async () => {
  try {
    const res = await fetch('/api/models')
    const data = await res.json()
    modelList.value = data.models || []
    if (modelList.value.length > 0) selectedModel.value = modelList.value[6]
  } catch {
    modelList.value = [
      'gpt-oss:20b',
      'deepseek-r1:8b',
      'gemma3n:e4b',
      'llama3.1:8b',
      'llama2:latest',
      'gemma2:2b'
    ]
    selectedModel.value = modelList.value[0]
  }

  try {
    const res = await fetch('/api/prompt_config')
    const data = await res.json()
    prompts.value = data.prompts || []
  } catch (error) {
    console.error('获取预设提示失败:', error)
    prompts.value = []
  }
})

// marked 配置代码高亮
marked.setOptions({
  highlight: function (code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  }
})

function flushAnswer(i, answerBuffer, isAnswer = true) {
  const answerMd = marked.parse(answerBuffer)
  if (isAnswer) {
    if (chainNodes.value[i]) {
      chainNodes.value[i].answer = answerMd
    } else {
      chainNodes.value.push({ answer: answerMd })
    }
  } else {
    if (chainNodes.value[i]) {
      chainNodes.value[i].summary = answerMd
    } else {
      chainNodes.value.push({ summary: answerMd })
    }
  }
  nextTick(() => {
    document.querySelectorAll('.chain-node pre code').forEach(block => hljs.highlightElement(block))
  })
}

// 链式调用接口，每步都把之前的答案附加到问题内容，流式返回
async function startChain() {
  chainNodes.value = []
  loading.value = true
  let prompt = projectDesc.value + '\n中文回答，字数尽量少,但不少于1000字，但需要完整输出答案。\n' + prompts.value[0] + ' 思考如何不多于 ' + (stepCount.value - 1) + ' 步骤 （可以减少步骤）完成这个项目的demo？\n'
  firstAnswer.value = await fetchStreamAnswer(prompt, selectedModel.value, flushAnswer, 0, true)
  let projectManage = firstAnswer.value
  let demand = ''
  let techDesign = ''
  for (let i = 1; i < stepCount.value; i++) {
    let sourcePrompt = ''
    if (prompts.value[i].includes('产品经理')) {
      sourcePrompt = projectManage + '\n'
    } else if (prompts.value[i].includes('架构师')) {
      sourcePrompt = demand + '\n'
    } else if (prompts.value[i].includes('开发者')) {
      sourcePrompt = demand + '\n\n' +techDesign + '\n'
    } else if (prompts.value[i].includes('测试人员')) {
      sourcePrompt = demand + '\n\n' +techDesign + '\n'
    }
    prompt = '第 ' + i + '步：' + sourcePrompt + prompts.value[i] + ' 请完成你要做的事情！\n中文回答，字数尽量少，但不少于3000字且要完整输出答案【要避免答案与问题内容重叠或者重复】！！！'
    // console.log('prompt: ' + prompt)
    // 获取链式节点答案
    const answerBuffer = await fetchStreamAnswer(prompt, selectedModel.value, flushAnswer, i, true)
      .then((buffer) => {
        return buffer
      })

    if (prompts.value[i].includes('产品经理')) {
      demand = answerBuffer
    } else if (prompts.value[i].includes('架构师')) {
      techDesign = answerBuffer
    }

    if (!answerBuffer || answerBuffer.trim() === '' || answerBuffer.trim().includes('答案生成完毕')) {
      console.log('链式分析已完成或无更多内容')
      loading.value = false
      break
    }
  }
  loading.value = false
}
</script>

<style scoped>
.project-engine {
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

.input-area {
  width: 80vw;
  max-width: 900px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 0 0;
}

.input-row {
  width: 100%;
  display: flex;
}

.input-row input {
  flex: 1;
  padding: 12px;
  font-size: 1em;
  border-radius: 6px;
  border: 1px solid #ccc;
  background: #f8f8fa;
}

.select-row {
  width: 100%;
  display: flex;
  gap: 12px;
  align-items: center;
}

.model-select {
  flex: 2;
  padding: 12px;
  font-size: 1em;
  border-radius: 6px;
  border: 1px solid #ccc;
  background: #f8f8fa;
}

.step-input {
  flex: 1;
  padding: 12px;
  font-size: 1em;
  border-radius: 6px;
  border: 1px solid #ccc;
  background: #f8f8fa;
  width: 100px;
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

.chain-result {
  width: 80vw;
  max-width: 66vw;
  margin-bottom: 48px;
}

.chain-node {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  padding: 12px;
  margin-bottom: 12px;
  margin-top: 20px;
}

.prompts-list {
  background: #eaa08d;
  padding: 2px;
}

.prompt-item {
  font-size: 1em;
  font-weight: bold;
  text-align: left;
  margin-top: 2px;
  background: #ddccc8;
}
</style>
