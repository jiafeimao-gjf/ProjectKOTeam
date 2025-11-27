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
      
      <div v-if="response" class="response-section">
        <h3>AI 分析结果</h3>
        <div class="response-content" v-html="renderedResponse"></div>
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

    const response = await fetch('/api/image_chat', {
      method: 'POST',
      body: formData,
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    if (result.code === 0) {
      response.value = result.content;
    } else {
      throw new Error(result.msg || 'API请求失败');
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
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
  background: #f4f6fb;
  display: flex;
  flex-direction: column;
}

.image-chat-page h2 {
  margin-top: 0;
  margin-bottom: 24px;
  font-size: 1.8em;
  font-weight: 600;
  color: #333;
  text-align: center;
}

.chat-container {
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid #e1e4e8;
}

.upload-area {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s;
  margin-bottom: 20px;
}

.upload-area:hover {
  border-color: #4f8cff;
}

.upload-placeholder {
  color: #888;
}

.upload-icon {
  font-size: 3em;
  margin-bottom: 10px;
}

.file-hint {
  font-size: 0.9em;
  color: #aaa;
}

.image-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.preview-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  object-fit: contain;
  margin-bottom: 15px;
}

.image-info {
  text-align: center;
  width: 100%;
}

.image-info p {
  margin: 5px 0;
}

.file-size {
  color: #888;
  font-size: 0.9em;
}

.remove-btn {
  margin-top: 10px;
  padding: 6px 12px;
  background: #f8f9fa;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
}

.remove-btn:hover {
  background: #e9ecef;
}

.prompt-section {
  margin-bottom: 20px;
}

.prompt-input {
  width: 100%;
  min-height: 100px;
  padding: 12px;
  font-size: 1em;
  border-radius: 6px;
  border: 1px solid #ccc;
  background: #f8f8fa;
  resize: vertical;
  font-family: inherit;
  box-sizing: border-box;
}

.model-selection {
  display: flex;
  gap: 12px;
  margin-top: 12px;
  align-items: center;
}

.model-select {
  flex: 1;
  padding: 10px;
  font-size: 1em;
  border-radius: 6px;
  border: 1px solid #ccc;
  background: #f8f8fa;
}

.submit-btn {
  padding: 10px 20px;
  font-size: 1em;
  border-radius: 6px;
  border: none;
  background: #4f8cff;
  color: #fff;
  cursor: pointer;
  transition: background 0.2s;
  min-width: 80px;
}

.submit-btn:hover:not(:disabled) {
  background: #3a7bff;
}

.submit-btn:disabled {
  background: #b0c4e6;
  cursor: not-allowed;
}

.loading-section, .error-section, .response-section {
  margin-top: 20px;
  padding: 16px;
  border-radius: 6px;
}

.loading-section {
  background: #e8f4ff;
  text-align: center;
}

.error-section {
  background: #ffe8e8;
  color: #d00;
}

.response-section {
  background: #f8f9fa;
  border: 1px solid #e1e4e8;
}

.response-section h3 {
  margin-top: 0;
  margin-bottom: 12px;
  color: #333;
}

.response-content {
  line-height: 1.6;
  text-align: left;
}

.response-content :deep(*) {
  text-align: left !important;
}

.response-content :deep(h1),
.response-content :deep(h2),
.response-content :deep(h3),
.response-content :deep(h4),
.response-content :deep(h5),
.response-content :deep(h6) {
  margin-top: 1.2em;
  margin-bottom: 0.8em;
  color: #2c3e50;
  text-align: left;
}

.response-content :deep(pre) {
  background: #f8f8f8;
  border-radius: 4px;
  padding: 12px;
  overflow-x: auto;
  margin: 12px 0;
  text-align: left;
}

.response-content :deep(code) {
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 0.9em;
  text-align: left;
}

.response-content :deep(pre code) {
  background: none;
  padding: 0;
  border-radius: 0;
  text-align: left;
}

.response-content :deep(blockquote) {
  border-left: 4px solid #4f8cff;
  padding-left: 16px;
  margin: 12px 0;
  color: #666;
  text-align: left;
}

.response-content :deep(a) {
  color: #4f8cff;
  text-decoration: none;
}

.response-content :deep(a:hover) {
  text-decoration: underline;
}

.response-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
  text-align: left;
}

.response-content :deep(th),
.response-content :deep(td) {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}
</style>