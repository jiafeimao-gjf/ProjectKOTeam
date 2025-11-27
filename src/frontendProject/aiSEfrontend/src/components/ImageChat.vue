<template>
  <div class="image-chat-page">
    <h2>图片对话</h2>
    
    <div class="chat-container">
      <div class="image-upload-section">
        <div 
          class="upload-area" 
          @dragover.prevent="onDragOver" 
          @drop.prevent="onDrop"
          @click="triggerFileSelect"
        >
          <div v-if="!selectedImage" class="upload-placeholder">
            <div class="upload-icon">📁</div>
            <p>拖拽图片到此处或点击选择图片</p>
            <p class="file-hint">支持 JPG, PNG, GIF 等常见图片格式</p>
          </div>
          <div v-else class="image-preview">
            <img :src="imagePreviewUrl" alt="预览图片" class="preview-image" />
            <div class="image-info">
              <p>{{ selectedImage.name }}</p>
              <p class="file-size">{{ formatFileSize(selectedImage.size) }}</p>
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
      
      <div class="prompt-section">
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
            <span v-else>提交</span>
          </button>
        </div>
      </div>
      
      <div v-if="isLoading" class="loading-section">
        <p>正在分析图片...</p>
      </div>
      
      <div v-if="error" class="error-section">
        <p class="error">{{ error }}</p>
      </div>
      
      <div class="response-section">
        <h3>AI 分析结果</h3>
        <div class="response-content" v-html="renderedResponse"></div>
        <div v-if="isSubmitting" class="streaming-indicator">AI正在分析中...</div>
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
  background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
  padding: var(--spacing);
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
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-xl);
  align-items: start;
}

/* 图片上传区域 */
.image-upload-section {
  background: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-lg);
  transition: all var(--transition);
  border: 2px solid var(--border-medium);
}

.image-upload-section:hover {
  box-shadow: var(--shadow-xl);
  border-color: var(--border-dark);
}

.upload-area {
  border: 3px dashed var(--border-medium);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xxl);
  text-align: center;
  cursor: pointer;
  transition: all var(--transition);
  background: var(--bg-secondary);
  position: relative;
  overflow: hidden;
}

.upload-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at center, rgba(79, 140, 255, 0.05) 0%, transparent 70%);
  opacity: 0;
  transition: opacity var(--transition);
}

.upload-area:hover,
.upload-area.dragover {
  border-color: var(--primary-color);
  background: var(--primary-light);
  transform: scale(1.02);
  border-style: solid;
}

.upload-area:hover::before,
.upload-area.dragover::before {
  opacity: 1;
}

.upload-placeholder {
  pointer-events: none;
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
  margin: var(--spacing-sm) 0;
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
}

.file-hint {
  font-size: var(--font-size-sm) !important;
  color: var(--text-muted) !important;
  font-weight: normal !important;
}

/* 图片预览 */
.image-preview {
  text-align: center;
}

.preview-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  margin-bottom: var(--spacing);
  object-fit: contain;
}

.image-info {
  background: var(--bg-secondary);
  padding: var(--spacing);
  border-radius: var(--border-radius);
}

.image-info p {
  margin: var(--spacing-xs) 0;
  color: var(--text-primary);
  font-weight: 500;
}

.file-size {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.remove-btn {
  background: var(--danger-color);
  color: var(--text-white);
  border: none;
  padding: var(--spacing-sm) var(--spacing);
  border-radius: var(--border-radius);
  cursor: pointer;
  margin-top: var(--spacing-sm);
  transition: all var(--transition);
  font-weight: 500;
}

.remove-btn:hover {
  background: #c82333;
  transform: translateY(-1px);
  box-shadow: var(--shadow);
}

/* 提示词输入区域 */
.prompt-section {
  background: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-lg);
  border: 2px solid var(--border-medium);
}

.prompt-input {
  width: 100%;
  min-height: 120px;
  margin-bottom: var(--spacing);
  padding: var(--spacing);
  border: 2px solid var(--border-medium);
  border-radius: var(--border-radius-lg);
  font-family: inherit;
  font-size: var(--font-size);
  background: var(--bg-primary);
  transition: all var(--transition);
  resize: vertical;
  box-sizing: border-box;
}

.prompt-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: var(--shadow), 0 0 0 3px rgba(79, 140, 255, 0.1);
}

.prompt-input:disabled {
  background: var(--gray-100);
  color: var(--text-muted);
  cursor: not-allowed;
}

.model-selection {
  display: flex;
  gap: var(--spacing);
  align-items: flex-end;
}

.model-select {
  flex: 1;
  padding: var(--spacing);
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: var(--font-size);
  background: var(--bg-primary);
  cursor: pointer;
  transition: all var(--transition);
  min-height: 50px;
}

.model-select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: var(--shadow), 0 0 0 3px rgba(79, 140, 255, 0.1);
}

.model-select:disabled {
  background: var(--gray-100);
  color: var(--text-muted);
  cursor: not-allowed;
}

.submit-btn {
  padding: var(--spacing) var(--spacing-lg);
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  color: var(--text-white);
  border: none;
  border-radius: var(--border-radius);
  font-size: var(--font-size);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition);
  min-height: 50px;
  position: relative;
  overflow: hidden;
  min-width: 100px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.submit-btn:disabled {
  background: linear-gradient(135deg, var(--gray-300), var(--gray-400));
  color: var(--text-muted);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 加载和错误状态 */
.loading-section,
.error-section {
  background: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
  margin: var(--spacing-lg) 0;
  text-align: center;
  box-shadow: var(--shadow);
  grid-column: 1 / -1;
}

.loading-section {
  background: linear-gradient(135deg, var(--primary-light), rgba(79, 140, 255, 0.1));
  border: 1px solid var(--primary-color);
}

.loading-section p {
  color: var(--primary-color);
  font-weight: 600;
  font-size: var(--font-size-lg);
  animation: pulse 1.5s ease-in-out infinite;
  margin: 0;
}

.error-section {
  background: linear-gradient(135deg, #fff5f5, rgba(220, 53, 69, 0.1));
  border: 1px solid var(--danger-color);
}

.error {
  color: var(--danger-color);
  font-weight: 600;
  margin: 0;
}

/* 响应区域 */
.response-section {
  background: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-lg);
  grid-column: 1 / -1;
  animation: fadeInUp 0.5s ease-out;
}

.response-section h3 {
  margin: 0 0 var(--spacing) 0;
  font-size: var(--font-size-xl);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.response-section h3::before {
  content: '✨';
  font-size: var(--font-size-lg);
}

.response-content {
  background: var(--bg-secondary);
  border-radius: var(--border-radius);
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing);
  min-height: 100px;
  max-height: 400px;
  overflow-y: auto;
  border-left: 4px solid var(--primary-color);
  line-height: 1.6;
}

.response-content::-webkit-scrollbar {
  width: 8px;
}

.response-content::-webkit-scrollbar-track {
  background: var(--bg-primary);
  border-radius: 4px;
}

.response-content::-webkit-scrollbar-thumb {
  background: var(--gray-400);
  border-radius: 4px;
}

.response-content::-webkit-scrollbar-thumb:hover {
  background: var(--gray-500);
}

.streaming-indicator {
  text-align: center;
  color: var(--primary-color);
  font-weight: 600;
  padding: var(--spacing);
  background: var(--primary-light);
  border-radius: var(--border-radius);
  animation: pulse 1.5s ease-in-out infinite;
  margin-top: var(--spacing);
}

/* Markdown内容样式 */
.response-content :deep(p) {
  margin: var(--spacing) 0;
  line-height: 1.7;
}

.response-content :deep(pre) {
  background: var(--bg-primary);
  border-radius: var(--border-radius);
  padding: var(--spacing);
  margin: var(--spacing) 0;
  overflow-x: auto;
  border-left: 3px solid var(--primary-color);
}

.response-content :deep(code) {
  background: var(--gray-100);
  padding: 2px 6px;
  border-radius: var(--border-radius-sm);
  font-family: var(--font-mono);
  font-size: var(--font-size-sm);
}

.response-content :deep(pre code) {
  background: none;
  padding: 0;
}

.response-content :deep(blockquote) {
  border-left: 4px solid var(--primary-color);
  padding-left: var(--spacing);
  margin: var(--spacing) 0;
  color: var(--text-secondary);
  font-style: italic;
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
}

.response-content :deep(th),
.response-content :deep(td) {
  border: 1px solid var(--border-color);
  padding: var(--spacing-sm);
  text-align: left;
}

.response-content :deep(th) {
  background: var(--bg-secondary);
  font-weight: 600;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .chat-container {
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
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
    padding: var(--spacing-sm);
  }
  
  h2 {
    font-size: var(--font-size-2xl);
    margin: var(--spacing) 0 var(--spacing-lg);
  }
  
  .upload-area {
    padding: var(--spacing-lg);
  }
  
  .upload-icon {
    font-size: 3rem;
  }
  
  .prompt-input {
    min-height: 100px;
  }
}

@media (max-width: 480px) {
  .upload-area {
    padding: var(--spacing);
  }
  
  .preview-image {
    max-height: 200px;
  }
  
  .response-content {
    max-height: 300px;
    padding: var(--spacing);
  }
}
</style>