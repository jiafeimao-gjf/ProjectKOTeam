<template>
  <div class="history-qa-page">
    <h2>历史问答记录</h2>

    <div v-if="loading" class="loading">
      正在加载历史记录...
    </div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <div v-else class="history-content">
      <div class="history-controls">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="搜索日期 (例如: 2025-08-09 或 20250809)"
          class="search-input"
        />
      </div>

      <div class="history-list">
        <div
          v-for="[date, files] in filteredHistoryList"
          :key="date"
          class="date-group"
        >
          <div
            class="date-header"
            @click="toggleDateGroup(date)"
          >
            <h3>{{ formatDate(date) }}</h3>
            <span class="toggle-icon">{{ isDateGroupExpanded(date) ? '−' : '+' }}</span>
          </div>

          <div v-show="isDateGroupExpanded(date)" class="date-content">
            <ul>
              <li
                v-for="file in files"
                :key="file"
                @click="loadHistoryContent(getFullFileName(date, file))"
                :class="{'active': selectedFile === getFullFileName(date, file)}"
                class="history-item"
              >
                <span class="file-name">{{ extractFileName(file) }}</span>
                <span class="timestamp">{{ extractTimestamp(file) }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div v-if="selectedHistoryContent" class="history-detail">
        <div class="content-area" v-html="renderedContent"></div>
      </div>

      <div v-else class="placeholder">
        <p>请选择一个历史记录查看内容</p>
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

// 响应式数据
const historyList = ref({});
const selectedFile = ref('');
const selectedHistoryContent = ref('');
const loading = ref(false);
const error = ref('');
const searchQuery = ref('');
const expandedDates = ref(new Set());

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
const renderedContent = computed(() => {
  if (!selectedHistoryContent.value) return '';
  const rawContent = marked.parse(selectedHistoryContent.value);
  return DOMPurify.sanitize(rawContent);
});

// 过滤后的历史列表（根据搜索查询）
const filteredHistoryList = computed(() => {
  // First, sort the history list by date (newest first)
  const sortedEntries = Object.entries(historyList.value).sort((a, b) => {
    // Extract the date-time string from the key
    let dateA = a[0];
    let dateB = b[0];

    // If it starts with 'history_', extract the date part
    if (dateA.startsWith('history_')) {
      dateA = dateA.replace('history_', '');
    }
    if (dateB.startsWith('history_')) {
      dateB = dateB.replace('history_', '');
    }

    // If it's in the format YYYYMMDDHHMMSS (like 20250809230906), convert to proper date format
    if (/^\d{14}$/.test(dateA)) {
      const dateAFormatted = `${dateA.substring(0, 4)}-${dateA.substring(4, 6)}-${dateA.substring(6, 8)} ${dateA.substring(8, 10)}:${dateA.substring(10, 12)}:${dateA.substring(12, 14)}`;
      dateA = dateAFormatted;
    }

    if (/^\d{14}$/.test(dateB)) {
      const dateBFormatted = `${dateB.substring(0, 4)}-${dateB.substring(4, 6)}-${dateB.substring(6, 8)} ${dateB.substring(8, 10)}:${dateB.substring(10, 12)}:${dateB.substring(12, 14)}`;
      dateB = dateBFormatted;
    }

    return new Date(dateB) - new Date(dateA);
  });

  // If no search query, return the sorted list
  if (!searchQuery.value.trim()) {
    return sortedEntries;
  }

  // Filter the entries based on the search query
  const query = searchQuery.value.trim().toLowerCase();
  return sortedEntries.filter(([date]) => {
    // Check if the date contains the search query in any format
    let dateForSearch = date;
    if (date.startsWith('history_')) {
      dateForSearch = date.substring(8); // Remove "history_" prefix
    }

    // Check various formats: YYYY-MM-DD, YYYYMMDD, MM/DD, etc.
    return (
      date.toLowerCase().includes(query) ||
      dateForSearch.toLowerCase().includes(query) ||
      dateForSearch.replace(/[-: ]/g, '').includes(query) || // Search in YYYYMMDDHHMMSS format
      dateForSearch.substring(0, 10).replace(/[-: ]/g, '').includes(query) // Search in YYYYMMDD format
    );
  });
});

// 检查日期组是否展开
const isDateGroupExpanded = (date) => {
  return expandedDates.value.has(date);
};

// 切换日期组展开/折叠状态
const toggleDateGroup = (date) => {
  if (expandedDates.value.has(date)) {
    expandedDates.value.delete(date);
  } else {
    expandedDates.value.add(date);
  }
};

// 格式化日期显示
const formatDate = (dateStr) => {
  // If it starts with 'history_', extract the date part
  let datePart = dateStr;
  if (dateStr.startsWith('history_')) {
    datePart = dateStr.substring(8); // 移除 "history_" 前缀
  }

  // If it's in the format YYYYMMDDHHMMSS (like 20250809230906), convert to readable format
  if (/^\d{14}$/.test(datePart)) {
    const year = datePart.substring(0, 4);
    const month = datePart.substring(4, 6);
    const day = datePart.substring(6, 8);
    const hour = datePart.substring(8, 10);
    const minute = datePart.substring(10, 12);
    const second = datePart.substring(12, 14);
    return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
  }

  return datePart;
};

// 提取文件名部分
const extractFileName = (fileName) => {
  // 例如：history_95368279-ef10-4c25-9415-df99721cfb33.md -> 95368279-ef10-4c25-9415-df99721cfb33
  const name = fileName.replace('history_', '').replace('.md', '');
  return name.substring(0, 8) + '...'; // 显示前8个字符后跟...
};

// 提取时间戳部分
const extractTimestamp = (fileName) => {
  // 从文件名中提取时间戳信息
  const regex = /history_([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.md/i;
  const match = fileName.match(regex);
  if (match) {
    return match[1].substring(0, 8); // 显示UUID的前8个字符
  }
  return fileName;
};

// 获取完整文件名
const getFullFileName = (dateStr, fileName) => {
  const datePart = dateStr.startsWith('history_') ? dateStr.substring(8) : dateStr;
  return `${datePart}/${fileName}`;
};

// 获取历史列表
const fetchHistoryList = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    const response = await fetch('/api/get_his_list');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    historyList.value = data;
  } catch (err) {
    console.error('获取历史记录列表失败:', err);
    error.value = '获取历史记录列表失败，请稍后重试。';
  } finally {
    loading.value = false;
  }
};

// 加载历史内容
const loadHistoryContent = async (fileName) => {
  selectedFile.value = fileName;
  loading.value = true;
  error.value = '';

  try {
    const response = await fetch(`/api/get_his_content?file_name=${encodeURIComponent(fileName)}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    
    if (data.code === 0) {
      // 处理内容，分离prompt和answer部分
      let content = data.content;
      
      // 在这里可以进一步处理内容格式，识别prompt和answer
      selectedHistoryContent.value = content;
    } else {
      throw new Error(data.msg || '获取历史内容失败');
    }
  } catch (err) {
    console.error('获取历史内容失败:', err);
    error.value = '获取历史内容失败，请稍后重试。';
    selectedHistoryContent.value = '';
  } finally {
    loading.value = false;
  }
};

// 页面初始化时获取历史列表
onMounted(async () => {
  await fetchHistoryList();
  
  // 在内容更新后应用代码高亮
  // 这里使用 watch 会在模板渲染后执行高亮
  const { nextTick, watch } = await import('vue');
  watch(selectedHistoryContent, async () => {
    await nextTick();
    document.querySelectorAll('.history-detail pre code').forEach(block => {
      hljs.highlightElement(block);
    });
  }, { immediate: true });
});
</script>

<style scoped>
.history-qa-page {
  min-height: 100vh;
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
  background: #f4f6fb;
  display: flex;
  flex-direction: column;
}

.history-qa-page h2 {
  margin-top: 0;
  margin-bottom: 24px;
  font-size: 1.8em;
  font-weight: 600;
  color: #333;
  text-align: center;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  font-size: 1.2em;
}

.error {
  color: #e74c3c;
}

.history-content {
  display: flex;
  flex: 1;
  gap: 20px;
  height: calc(100vh - 140px);
}

.search-input {
  width: 100%;
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

.history-list {
  width: 300px;
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  overflow-y: auto;
  border: 1px solid #e1e4e8;
}

.date-group {
  margin-bottom: 15px;
  border: 1px solid #e1e4e8;
  border-radius: 6px;
  overflow: hidden;
}

.date-header {
  padding: 10px 12px;
  background: #f8f9fa;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #333;
}

.date-header:hover {
  background: #e9ecef;
}

.toggle-icon {
  font-size: 1.2em;
  font-weight: bold;
  width: 20px;
  text-align: center;
  display: inline-block;
}

.date-content {
  padding: 10px;
  background: #fff;
}

.date-group ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.history-item {
  padding: 8px 10px;
  margin: 5px 0;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  border: 1px solid #e1e4e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-item:hover {
  background-color: #f0f5ff;
}

.history-item.active {
  background-color: #4f8cff;
  color: white;
  border-color: #4f8cff;
}

.file-name {
  font-weight: 500;
  flex: 1;
}

.timestamp {
  font-size: 0.8em;
  opacity: 0.7;
  margin-left: 8px;
}

.history-detail {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  overflow-y: auto;
  border: 1px solid #e1e4e8;
}

.content-area {
  line-height: 1.6;
  text-align: left;
}

.content-area :deep(*) {
  text-align: left !important;
}

.content-area :deep(h1),
.content-area :deep(h2),
.content-area :deep(h3),
.content-area :deep(h4),
.content-area :deep(h5),
.content-area :deep(h6) {
  margin-top: 1.2em;
  margin-bottom: 0.8em;
  color: #2c3e50;
  text-align: left;
}

.content-area :deep(pre) {
  background: #f8f8f8;
  border-radius: 4px;
  padding: 12px;
  overflow-x: auto;
  margin: 12px 0;
  text-align: left;
}

.content-area :deep(code) {
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 0.9em;
  text-align: left;
}

.content-area :deep(pre code) {
  background: none;
  padding: 0;
  border-radius: 0;
  text-align: left;
}

.content-area :deep(blockquote) {
  border-left: 4px solid #4f8cff;
  padding-left: 16px;
  margin: 12px 0;
  color: #666;
  text-align: left;
}

.content-area :deep(a) {
  color: #4f8cff;
  text-decoration: none;
}

.content-area :deep(a:hover) {
  text-decoration: underline;
}

.content-area :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
  text-align: left;
}

.content-area :deep(th),
.content-area :deep(td) {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}

.content-area :deep(th) {
  background-color: #f8f8f8;
  font-weight: bold;
}

.placeholder {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid #e1e4e8;
}

.placeholder p {
  font-size: 1.2em;
  color: #888;
}
</style>