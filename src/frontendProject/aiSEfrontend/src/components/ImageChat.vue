<template>
  <div class="image-chat-page">
    <h2>🖼️ 图片对话</h2>

    <div class="chat-container">
      <!-- 左侧图片上传区域 -->
      <div class="upload-panel">
        <h3 class="panel-title">📤 上传图片</h3>

        <div
          class="upload-area"
          @dragover.prevent="onDragOver"
          @drop.prevent="onDrop"
          @click="triggerFileSelect"
        >
          <div v-if="!selectedImage" class="upload-placeholder">
            <div class="upload-icon">🖼️</div>
            <p>拖拽图片到此处或点击选择图片</p>
            <p class="file-hint">支持 JPG, PNG, GIF 等常见图片格式（最大10MB）</p>
            <button class="upload-btn">选择图片</button>
          </div>

          <div v-else class="image-preview">
            <div class="preview-container">
              <img :src="imagePreviewUrl" alt="预览图片" class="preview-image" />
              <div class="image-overlay">
                <button @click="removeImage" class="remove-btn-overlay" title="移除图片">✕</button>
              </div>
            </div>

            <div class="image-info">
              <div class="file-details">
                <p class="file-name">{{ selectedImage.name }}</p>
                <p class="file-size">{{ formatFileSize(selectedImage.size) }}</p>
              </div>
              <button @click="removeImage" class="remove-btn">移除图片</button>
            </div>
          </div>

          <input
            type="file"
            ref="fileInput"
            @change="onFileChange"
            accept="image/*"
            style="display: none"
          />
        </div>
      </div>

      <!-- 右侧处理区域 -->
      <div class="process-panel">
        <!-- 提示词输入区域 -->
        <div class="prompt-section">
          <h3 class="panel-title">💬 输入提示词</h3>
          <textarea
            v-model="prompt"
            placeholder="请输入对图片的描述或问题..."
            class="prompt-input"
            :disabled="!selectedImage"
          ></textarea>

          <div class="model-selection">
            <select v-model="selectedModel" class="model-select" :disabled="!selectedImage">
              <option value="">选择模型</option>
              <option v-for="model in modelList" :key="model" :value="model">{{ model }}</option>
            </select>

            <button
              @click="submitImageChat"
              :disabled="!canSubmit"
              class="submit-btn"
            >
              <span v-if="isSubmitting">提交中...</span>
              <span v-else>🚀 分析图片</span>
            </button>
          </div>
        </div>

        <!-- 状态指示器 -->
        <div v-if="isLoading" class="status-section loading-section">
          <div class="status-icon">🔄</div>
          <p>正在分析图片...</p>
          <div class="progress-bar">
            <div class="progress-fill"></div>
          </div>
        </div>

        <div v-if="error" class="status-section error-section">
          <div class="status-icon">❌</div>
          <p class="error">{{ error }}</p>
        </div>

        <!-- AI 响应区域 -->
        <div class="response-section">
          <h3 class="panel-title">🤖 AI 分析结果</h3>
          <div class="response-content" v-html="renderedResponse"></div>
          <div v-if="isSubmitting" class="streaming-indicator">
            <span>AI正在分析中</span>
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { marked } from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css';
import DOMPurify from 'dompurify';

const fileInput = ref(null);
const selectedImage = ref(null);
const imagePreviewUrl = ref('');
const prompt = ref('');
const response = ref('');
const isLoading = ref(false);
const error = ref('');
const isSubmitting = ref(false);
const modelList = ref([]);
const selectedModel = ref('');

// 配置 marked 以支持代码高亮
marked.setOptions({
  highlight: function (code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value;
    }
    return hljs.highlightAuto(code).value;
  },
  gfm: true,
  breaks: true
});

// 渲染内容，使用 DOMPurify 净化 HTML
const renderedResponse = computed(() => {
  if (!response.value) return '';
  const rawContent = marked.parse(response.value);
  return DOMPurify.sanitize(rawContent);
});

// 是否可以提交
const canSubmit = computed(() => {
  return selectedImage.value && 
         prompt.value.trim() && 
         selectedModel.value && 
         !isLoading.value && 
         !isSubmitting.value;
});

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// 触发文件选择
const triggerFileSelect = () => {
  fileInput.value.click();
};

// 处理文件选择
const onFileChange = (event) => {
  const files = event.target.files;
  if (files && files[0]) {
    handleSelectedFile(files[0]);
  }
};

// 处理拖拽文件
const onDragOver = (event) => {
  event.preventDefault();
};

// 处理拖拽放置
const onDrop = (event) => {
  event.preventDefault();
  const files = event.dataTransfer.files;
  if (files && files[0]) {
    handleSelectedFile(files[0]);
  }
};

// 处理选中的文件
const handleSelectedFile = (file) => {
  // 检查是否为图片文件
  if (!file.type.startsWith('image/')) {
    error.value = '请选择图片文件 (JPG, PNG, GIF 等)';
    return;
  }
  
  // 检查文件大小 (限制为10MB)
  if (file.size > 10 * 1024 * 1024) {
    error.value = '图片文件大小不能超过 10MB';
    return;
  }
  
  selectedImage.value = file;
  imagePreviewUrl.value = URL.createObjectURL(file);
  error.value = '';
};

// 移除图片
const removeImage = () => {
  selectedImage.value = null;
  imagePreviewUrl.value = '';
  response.value = '';
  error.value = '';
};

// 获取模型列表
const fetchModelList = async () => {
  try {
    const res = await fetch('/api/models');
    const data = await res.json();
    modelList.value = data.models || [];
    // 默认选中第一个模型
    if (modelList.value.length > 0) {
      selectedModel.value = modelList.value[0];
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
    ];
    selectedModel.value = modelList.value[0];
  }
};

// 提交图片对话请求
const submitImageChat = async () => {
  if (!canSubmit.value) return;

  isSubmitting.value = true;
  error.value = '';
  response.value = '';
  isLoading.value = true;

  try {
    const formData = new FormData();
    formData.append('image', selectedImage.value);
    formData.append('prompt', prompt.value);
    if (selectedModel.value) {
      formData.append('model', selectedModel.value);
    }

    // Create abort controller for timeout handling
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 20 * 60 * 1000); // 20 minutes

    const apiResponse = await fetch('/api/image_chat', {
      method: 'POST',
      body: formData,
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!apiResponse.ok) {
      throw new Error(`HTTP error! status: ${apiResponse.status}`);
    }

    // Check if the response is in text/event-stream format for streaming
    const contentType = apiResponse.headers.get('Content-Type');

    if (contentType && contentType.includes('text/event-stream')) {
      // Handle streaming response
      const reader = apiResponse.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // Keep last incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6); // Remove 'data: ' prefix
            if (data === '[DONE]') {
              isSubmitting.value = false;
              isLoading.value = false;
              return;
            }

            try {
              const parsed = JSON.parse(data);
              if (parsed.text) {
                response.value += parsed.text;
              }
            } catch (e) {
              // If JSON parsing fails, add raw data to response
              if (data.trim()) {
                response.value += data;
              }
            }
          }
        }
      }
    } else {
      // Handle regular JSON response
      const result = await apiResponse.json();
      if (result.code === 0) {
        response.value = result.content;
      } else {
        throw new Error(result.msg || 'API请求失败');
      }
    }
  } catch (err) {
    console.error('提交图片对话请求失败:', err);
    if (err.name === 'AbortError') {
      error.value = '请求超时: 图片分析已运行超过20分钟，请重试。';
    } else {
      error.value = `提交请求失败: ${err.message}`;
    }
  } finally {
    isSubmitting.value = false;
    isLoading.value = false;
  }
};

// 页面初始化时获取模型列表
onMounted(async () => {
  await fetchModelList();
});
</script>

<style scoped>
.image-chat-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4edf9 100%);
  padding: var(--spacing-lg);
  box-sizing: border-box;
}

h2 {
  text-align: center;
  margin: var(--spacing-lg) 0 var(--spacing-xl);
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--text-primary);
  position: relative;
}

h2::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 3px;
  background: linear-gradient(90deg, var(--primary-color), var(--primary-hover));
  border-radius: 2px;
}

.chat-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  gap: var(--spacing-xl);
  align-items: flex-start;
}

/* 面板标题 */
.panel-title {
  margin: 0 0 var(--spacing-lg) 0;
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding-bottom: var(--spacing-sm);
  border-bottom: 2px solid var(--border-light);
  background: linear-gradient(to right, var(--primary-color), var(--primary-hover));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-fill-color: transparent;
}

/* 上传面板 */
.upload-panel {
  flex: 1;
  background: linear-gradient(145deg, #ffffff, #f0f4f8);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-lg);
  box-shadow:
    0 4px 6px rgba(0, 0, 0, 0.05),
    0 1px 3px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(0, 0, 0, 0.05);
  max-width: 500px;
  backdrop-filter: blur(10px);
}

/* 处理面板 */
.process-panel {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  background: linear-gradient(145deg, #f8fafc, #e6f0f7);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-lg);
  box-shadow:
    0 4px 6px rgba(0, 0, 0, 0.05),
    0 1px 3px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(10px);
}

/* 图片上传区域 */
.upload-area {
  border: 3px dashed #c5d9eb;
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xxl);
  text-align: center;
  cursor: pointer;
  transition: all var(--transition);
  background: linear-gradient(to bottom, #f8fafc, #e6f0f7);
  position: relative;
  overflow: hidden;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at center, rgba(120, 180, 240, 0.1) 0%, transparent 70%);
  opacity: 0;
  transition: opacity var(--transition);
}

.upload-area:hover,
.upload-area.dragover {
  border-color: var(--primary-color);
  background: linear-gradient(to bottom, #e6f0ff, #d0e3ff);
  transform: translateY(-2px);
  box-shadow:
    0 10px 25px -5px rgba(79, 140, 255, 0.2),
    0 8px 10px -6px rgba(79, 140, 255, 0.2);
  border-style: solid;
}

.upload-area:hover::before,
.upload-area.dragover::before {
  opacity: 1;
}

.upload-placeholder {
  pointer-events: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: var(--spacing);
}

.upload-icon {
  font-size: 4rem;
  margin-bottom: var(--spacing);
  opacity: 0.6;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.upload-placeholder p {
  margin: var(--spacing-xs) 0;
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
}

.file-hint {
  font-size: var(--font-size-sm) !important;
  color: var(--text-muted) !important;
  font-weight: normal !important;
}

.upload-btn {
  margin-top: var(--spacing);
  padding: var(--spacing-sm) var(--spacing-lg);
  background: linear-gradient(to right, var(--primary-color), var(--primary-hover));
  color: white;
  border: none;
  border-radius: var(--border-radius-lg);
  cursor: pointer;
  font-weight: 600;
  transition: all var(--transition);
  font-size: var(--font-size);
  box-shadow: 0 4px 6px rgba(79, 140, 255, 0.2);
}

.upload-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(79, 140, 255, 0.3);
}

/* 图片预览 */
.image-preview {
  display: flex;
  flex-direction: column;
  gap: var(--spacing);
}

.preview-container {
  position: relative;
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.preview-image {
  width: 100%;
  height: 250px;
  object-fit: contain;
  display: block;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.25);
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  padding: var(--spacing-sm);
  opacity: 0;
  transition: opacity var(--transition);
}

.preview-container:hover .image-overlay {
  opacity: 1;
}

.remove-btn-overlay {
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  border: none;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-weight: bold;
  transition: all var(--transition);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.remove-btn-overlay:hover {
  background: rgba(220, 53, 69, 0.9);
  color: white;
  transform: scale(1.1);
}

.image-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(240, 244, 248, 0.7);
  padding: var(--spacing);
  border-radius: var(--border-radius-lg);
  margin-top: var(--spacing-sm);
  backdrop-filter: blur(5px);
}

.file-details {
  flex: 1;
}

.file-name {
  margin: 0 0 var(--spacing-xs) 0;
  font-weight: 600;
  color: var(--text-primary);
  word-break: break-all;
}

.file-size {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin: 0;
}

.remove-btn {
  background: linear-gradient(to right, #dc3545, #c82333);
  color: white;
  border: none;
  padding: var(--spacing-sm) var(--spacing);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all var(--transition);
  font-weight: 500;
  align-self: flex-start;
  box-shadow: 0 4px 6px rgba(220, 53, 69, 0.2);
}

.remove-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 12px rgba(220, 53, 69, 0.3);
}

/* 提示词输入区域 */
.prompt-section {
  background: rgba(255, 255, 255, 0.7);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-lg);
  box-shadow:
    0 4px 6px rgba(0, 0, 0, 0.05),
    0 1px 3px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(10px);
}

.prompt-input {
  width: 100%;
  min-height: 150px;
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-lg);
  border: 2px solid #d0e0f0;
  border-radius: var(--border-radius-lg);
  font-family: inherit;
  font-size: var(--font-size);
  background: rgba(255, 255, 255, 0.8);
  transition: all var(--transition);
  resize: vertical;
  box-sizing: border-box;
}

.prompt-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow:
    0 0 0 3px rgba(79, 140, 255, 0.1),
    0 0 10px rgba(79, 140, 255, 0.2);
}

.prompt-input:disabled {
  background: rgba(240, 244, 248, 0.5);
  color: var(--text-muted);
  cursor: not-allowed;
}

.model-selection {
  display: flex;
  gap: var(--spacing);
  align-items: center;
}

.model-select {
  flex: 1;
  padding: var(--spacing-md);
  border: 2px solid #d0e0f0;
  border-radius: var(--border-radius);
  font-size: var(--font-size);
  background: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all var(--transition);
  min-height: 50px;
}

.model-select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow:
    0 0 0 3px rgba(79, 140, 255, 0.1),
    0 0 10px rgba(79, 140, 255, 0.2);
}

.model-select:disabled {
  background: rgba(240, 244, 248, 0.5);
  color: var(--text-muted);
  cursor: not-allowed;
}

.submit-btn {
  padding: var(--spacing-md) var(--spacing-xl);
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  color: white;
  border: none;
  border-radius: var(--border-radius-lg);
  font-size: var(--font-size);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition);
  min-height: 50px;
  position: relative;
  overflow: hidden;
  min-width: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  box-shadow: 0 4px 15px rgba(79, 140, 255, 0.3);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(79, 140, 255, 0.4);
}

.submit-btn:disabled {
  background: linear-gradient(135deg, #a0aec0, #cbd5e0);
  color: white;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 状态指示器 */
.status-section {
  background: rgba(255, 255, 255, 0.7);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-lg);
  box-shadow:
    0 4px 6px rgba(0, 0, 0, 0.05),
    0 1px 3px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing);
  backdrop-filter: blur(10px);
}

.status-icon {
  font-size: var(--font-size-3xl);
}

.loading-section {
  background: linear-gradient(135deg, rgba(79, 140, 255, 0.1), rgba(120, 180, 255, 0.1));
  border: 1px solid rgba(79, 140, 255, 0.2);
}

.error-section {
  background: linear-gradient(135deg, rgba(220, 53, 69, 0.1), rgba(248, 120, 140, 0.1));
  border: 1px solid rgba(220, 53, 69, 0.2);
}

.error {
  color: #c82333;
  font-weight: 600;
  margin: 0;
  text-align: center;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
}

.progress-fill {
  height: 100%;
  width: 60%;
  background: linear-gradient(90deg, var(--primary-color), var(--primary-hover));
  border-radius: 4px;
  animation: progress 2s infinite ease-in-out;
}

@keyframes progress {
  0% { width: 0%; }
  50% { width: 100%; }
  100% { width: 0%; }
}

/* 响应区域 */
.response-section {
  background: rgba(255, 255, 255, 0.7);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-lg);
  box-shadow:
    0 4px 6px rgba(0, 0, 0, 0.05),
    0 1px 3px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(0, 0, 0, 0.05);
  flex: 1;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(10px);
}

.response-content {
  flex: 1;
  background: rgba(240, 244, 248, 0.5);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;
  border-left: 4px solid var(--primary-color);
  line-height: 1.6;
  flex-grow: 1;
}

.response-content::-webkit-scrollbar {
  width: 8px;
}

.response-content::-webkit-scrollbar-track {
  background: rgba(240, 244, 248, 0.7);
  border-radius: 4px;
}

.response-content::-webkit-scrollbar-thumb {
  background: #c5d9eb;
  border-radius: 4px;
}

.response-content::-webkit-scrollbar-thumb:hover {
  background: #a0c4e3;
}

.streaming-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing);
  color: var(--primary-color);
  font-weight: 600;
  padding: var(--spacing-lg);
  background: rgba(79, 140, 255, 0.1);
  border-radius: var(--border-radius-lg);
  margin-top: var(--spacing-lg);
  border: 1px dashed var(--primary-color);
  backdrop-filter: blur(10px);
}

.typing-indicator {
  display: flex;
  gap: var(--spacing-xs);
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--primary-color);
  border-radius: 50%;
  display: inline-block;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: 0s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-5px); }
}

/* Markdown内容样式 */
.response-content :deep(p) {
  margin: var(--spacing) 0;
  line-height: 1.7;
}

.response-content :deep(pre) {
  background: rgba(255, 255, 255, 0.8);
  border-radius: var(--border-radius);
  padding: var(--spacing);
  margin: var(--spacing) 0;
  overflow-x: auto;
  border-left: 3px solid var(--primary-color);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.response-content :deep(code) {
  background: rgba(240, 244, 248, 0.7);
  padding: 2px 6px;
  border-radius: var(--border-radius-sm);
  font-family: var(--font-mono);
  font-size: var(--font-size-sm);
  border: 1px solid #d0e0f0;
}

.response-content :deep(pre code) {
  background: none;
  padding: 0;
  border: none;
}

.response-content :deep(blockquote) {
  border-left: 4px solid var(--primary-color);
  padding-left: var(--spacing);
  margin: var(--spacing) 0;
  color: var(--text-secondary);
  font-style: italic;
  background: rgba(240, 244, 248, 0.5);
  padding: var(--spacing);
  border-radius: var(--border-radius);
}

.response-content :deep(h1),
.response-content :deep(h2),
.response-content :deep(h3),
.response-content :deep(h4),
.response-content :deep(h5),
.response-content :deep(h6) {
  margin-top: var(--spacing-lg);
  margin-bottom: var(--spacing);
  color: var(--text-primary);
  font-weight: 600;
}

.response-content :deep(a) {
  color: var(--primary-color);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.response-content :deep(a:hover) {
  color: var(--primary-hover);
  text-decoration: underline;
}

.response-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: var(--spacing) 0;
  border: 1px solid #d0e0f0;
}

.response-content :deep(th),
.response-content :deep(td) {
  border: 1px solid #d0e0f0;
  padding: var(--spacing-sm);
  text-align: left;
}

.response-content :deep(th) {
  background: rgba(240, 244, 248, 0.7);
  font-weight: 600;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .chat-container {
    flex-direction: column;
  }

  .upload-panel {
    max-width: 100%;
  }

  .model-selection {
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .model-select,
  .submit-btn {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .image-chat-page {
    padding: var(--spacing);
  }

  h2 {
    font-size: var(--font-size-2xl);
    margin: var(--spacing) 0 var(--spacing-lg);
  }

  .upload-area {
    padding: var(--spacing-lg);
    min-height: 250px;
  }

  .upload-icon {
    font-size: 3rem;
  }

  .prompt-input {
    min-height: 120px;
  }

  .image-info {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }

  .remove-btn {
    align-self: flex-end;
  }
}

@media (max-width: 480px) {
  .upload-area {
    padding: var(--spacing);
  }

  .preview-image {
    height: 200px;
  }

  .response-content {
    max-height: 300px;
    padding: var(--spacing);
  }

  .model-selection {
    flex-direction: column;
  }

  .submit-btn {
    min-width: 100%;
  }
}
</style>